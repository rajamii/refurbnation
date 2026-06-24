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

  newSlot = {
    date: '',
    start_time: '09:00:00',
    end_time: '12:00:00',
    max_capacity: 2
  };

  statusOptions = ['PENDING', 'CONFIRMED', 'IN_PROGRESS', 'READY', 'COMPLETED', 'CANCELLED'];

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router
  ) { }

  ngOnInit() {
    this.loadAllSystemBookings();
  }

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${localStorage.getItem('access')}`);
  }

  loadAllSystemBookings() {
    this.http.get(`${this.baseApi}/bookings/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.allBookings = res,
        error: (err) => console.error('Failed to load active shop pipeline', err)
      });
  }

  createSlot() {
    if (!this.newSlot.date) return;

    this.http.post(`${this.baseApi}/slots/`, this.newSlot, { headers: this.getHeaders() })
      .subscribe({
        next: () => {
          alert(`Available slots for ${this.newSlot.date} published to clients.`);
          this.newSlot.date = '';
        },
        error: (err) => console.error('Slot construction failure', err)
      });
  }

  confirmBooking(bookingId: number) {
    this.updateBookingPayload(bookingId, { status: 'CONFIRMED' });
  }

  updateBookingPayload(bookingId: number, updateData: { status?: string, estimated_delivery_timeline?: string }) {
    this.http.patch(`${this.baseApi}/bookings/${bookingId}/update_status/`, updateData, { headers: this.getHeaders() })
      .subscribe({
        next: () => this.loadAllSystemBookings(),
        error: (err) => console.error('Failed to save assignment updates', err)
      });
  }

  modifyBookingDetails(bookingId: number, serviceId: number, slotId: number) {
    const fullPayload = { service: serviceId, slot: slotId };


    this.http.patch(`${this.baseApi}/bookings/${bookingId}/`, fullPayload, { headers: this.getHeaders() })
      .subscribe(() => this.loadAllSystemBookings());
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}