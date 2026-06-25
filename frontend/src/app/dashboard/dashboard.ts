import { Component, OnInit, OnDestroy } from '@angular/core';
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
export class Dashboard implements OnInit, OnDestroy {
  private baseApi = 'http://localhost:8000/api';
  private pollingTimer: any;
  
  services: any[] = [];
  bookings: any[] = [];
  masterCategories: any[] = [];

  selectedServiceId: number | null = null;
  selectedCategoryCode: string = '';
  requestedDate: string = '';
  vehicleMakeModel: string = '';
  vehicleLicensePlate: string = '';
  currentQuotePrice: number | null = null;

  constructor(
    private http: HttpClient, 
    private authService: AuthService, 
    private router: Router
  ) {}

  ngOnInit() {
    this.loadMasterConfigurations();
    this.loadServices();
    this.loadMyBookings();

    // Background loop refresh tracker execution
    this.pollingTimer = setInterval(() => {
      this.loadMyBookings();
    }, 15000);
  }

  ngOnDestroy() {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
    }
  }

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${localStorage.getItem('access')}`);
  }

  loadMasterConfigurations() {
    this.http.get(`${this.baseApi}/config/meta_lookup/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.masterCategories = res.categories,
        error: (err) => console.error('Failed to clear master table lookup configuration matrix', err)
      });
  }

  loadServices() {
    this.http.get(`${this.baseApi}/services/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.services = res,
        error: (err) => console.error('Failed to pull studio services matrix', err)
      });
  }

  calculateLiveQuote() {
    if (!this.selectedServiceId || !this.selectedCategoryCode) {
      this.currentQuotePrice = null;
      return;
    }
    const targetService = this.services.find(s => s.id === this.selectedServiceId);
    if (targetService && targetService.prices) {
      const rateMatch = targetService.prices.find((p: any) => p.category_code === this.selectedCategoryCode);
      this.currentQuotePrice = rateMatch ? rateMatch.price_in_rupees : 0;
    }
  }

  loadMyBookings() {
    this.http.get(`${this.baseApi}/bookings/`, { headers: this.getHeaders() })
      .subscribe({
        next: (res: any) => this.bookings = res,
        error: (err) => console.error('Failed to load tracking records', err)
      });
  }

  createBooking() {
    if (!this.selectedServiceId || !this.selectedCategoryCode || !this.requestedDate || !this.vehicleMakeModel) return;

    const payload = {
      service: this.selectedServiceId,
      vehicle_category: this.selectedCategoryCode,
      requested_date: this.requestedDate,
      vehicle_make_model: this.vehicleMakeModel,
      vehicle_license_plate: this.vehicleLicensePlate || null
    };

    this.http.post(`${this.baseApi}/bookings/`, payload, { headers: this.getHeaders() })
      .subscribe({
        next: () => {
          this.selectedServiceId = null;
          this.selectedCategoryCode = '';
          this.requestedDate = '';
          this.vehicleMakeModel = '';
          this.vehicleLicensePlate = '';
          this.currentQuotePrice = null;
          this.loadMyBookings();
        },
        error: (err) => console.error('Booking placement validation failed', err)
      });
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}