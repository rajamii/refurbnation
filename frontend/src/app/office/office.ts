import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-office',
  templateUrl: './office.html',
  standalone: true,
  imports: [CommonModule, FormsModule]
})
export class Office implements OnInit {
  private baseApi = 'http://localhost:8000/api';

  allBookings: any[] = [];
  availableSlots: any[] = [];
  masterStatuses: any[] = [];

  newSlot = {
    date: '',
    start_time: '09:00:00',
    end_time: '12:00:00',
    max_capacity: 2
  };

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router
  ) { }

  ngOnInit() {
    this.loadMasterConfigurations();
    this.loadAllSystemBookings();
    this.loadActiveAvailableSlots();
  }

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${localStorage.getItem('access')}`);
  }

  loadMasterConfigurations() {
    this.http.get(`${this.baseApi}/config/meta_lookup/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.masterStatuses = res.statuses,
        error: (err) => console.error('Failed to parse status list parameters', err)
      });
  }

  loadAllSystemBookings() {
    this.http.get(`${this.baseApi}/bookings/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.allBookings = res,
        error: (err) => console.error('Failed to load active shop pipeline', err)
      });
  }

  loadActiveAvailableSlots() {
    this.http.get(`${this.baseApi}/slots/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.availableSlots = res,
        error: (err) => console.error('Failed to parse calendar blocks', err)
      });
  }

  createSlot() {
    if (!this.newSlot.date) return;

    this.http.post(`${this.baseApi}/slots/`, this.newSlot, { headers: this.getHeaders() })
      .subscribe({
        next: () => {
          alert(`Available slots for ${this.newSlot.date} published to clients.`);
          this.newSlot.date = '';
          this.loadActiveAvailableSlots();
        },
        error: (err) => console.error('Slot construction failure', err)
      });
  }

  confirmAndAssignBooking(bookingItem: any) {
    const payload = {
      status: 'CONFIRMED',
      slot: bookingItem.targetSlotId,
      estimated_delivery_timeline: bookingItem.temp_delivery_timeline || ''
    };
    this.updateBookingPayload(bookingItem.id, payload);
  }

  updateBookingPayload(bookingId: number, updateData: { status?: string, slot?: number, estimated_delivery_timeline?: string }) {
    this.http.patch(`${this.baseApi}/bookings/${bookingId}/update_status/`, updateData, { headers: this.getHeaders() })
      .subscribe({
        next: () => this.loadAllSystemBookings(),
        error: (err) => console.error('Failed to save assignment updates', err)
      });
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}