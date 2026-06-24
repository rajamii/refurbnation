import { Component, OnInit, OnDestroy } from '@angular/core'; // <-- 1. Add OnDestroy
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit, OnDestroy { // <-- 2. Implement OnDestroy
  private baseApi = 'http://localhost:8000/api';
  private pollingTimer: any; // <-- Tracker loop reference
  
  services: any[] = [];
  slots: any[] = [];
  bookings: any[] = [];

  selectedServiceId: number | null = null;
  selectedSlotId: number | null = null;

  constructor(
    private http: HttpClient, 
    private authService: AuthService, 
    private router: Router
  ) {}

  ngOnInit() {
    this.loadServices();
    this.loadAvailableSlots();
    this.loadMyBookings();

    // 3. Auto-query the database background loop every 15 seconds
    this.pollingTimer = setInterval(() => {
      this.loadMyBookings();
    }, 15000);
  }

  // 4. Clear background thread allocations when user changes routes (Fixes Lighthouse cache bugs!)
  ngOnDestroy() {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
    }
  }

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${localStorage.getItem('access')}`);
  }

  loadServices() {
    this.http.get(`${this.baseApi}/services/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.services = res,
        error: (err) => console.error('Failed to pull studio services matrix', err)
      });
  }

  loadAvailableSlots() {
    this.http.get(`${this.baseApi}/slots/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.slots = res,
        error: (err) => console.error('Failed to pull calendar blocks', err)
      });
  }

  loadMyBookings() {
    this.http.get(`${this.baseApi}/bookings/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.bookings = res,
        error: (err) => console.error('Failed to load tracking records', err)
      });
  }

  createBooking() {
    if (!this.selectedServiceId || !this.selectedSlotId) return;

    const payload = {
      service: this.selectedServiceId,
      slot: this.selectedSlotId
    };

    this.http.post(`${this.baseApi}/bookings/`, payload, { headers: this.getHeaders() })
      .subscribe({
        next: () => {
          this.selectedServiceId = null;
          this.selectedSlotId = null;
          this.loadMyBookings();
        },
        error: (err) => console.error('Booking placement failed', err)
      });
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}