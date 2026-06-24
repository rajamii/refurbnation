import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.html',
  standalone: true,
  imports: [FormsModule, CommonModule]
})
export class AdminComponent implements OnInit {
  activeTab: 'clients' | 'office' | 'services' | 'logs' = 'clients';
  logs: any[] = [];
  users: any[] = [];
  services: any[] = [];

  newOfficeEmail = '';
  newOfficePassword = '';

  newService = {
    name: '',
    description: '',
    price: '',
    estimated_duration_hours: '1.0'
  };

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.refreshData();
  }

  setTab(tab: 'clients' | 'office' | 'services' | 'logs') {
    this.activeTab = tab;
    this.refreshData();
  }

  getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${localStorage.getItem('access')}`);
  }

  refreshData() {
  if (this.activeTab === 'services') {
    this.fetchServices();
  } else if (this.activeTab === 'logs') {
    this.fetchAuditLogs();
  } else {
    this.fetchUsers();
  }
}

  fetchUsers() {
    const roleMap = this.activeTab === 'clients' ? 'USER' : 'OFFICE';
    this.http.get(`http://localhost:8000/api/admin/users/?role=${roleMap}`, { headers: this.getHeaders() })
      .subscribe((data: any) => this.users = data);
  }

  createOfficeUser() {
    const payload = { email: this.newOfficeEmail, password: this.newOfficePassword };
    this.http.post('http://localhost:8000/api/admin/users/office/', payload, { headers: this.getHeaders() })
      .subscribe(() => {
        this.fetchUsers();
        this.newOfficeEmail = '';
        this.newOfficePassword = '';
      });
  }

  // --- Service Management Methods ---
  fetchServices() {
    this.http.get('http://localhost:8000/api/services/', { headers: this.getHeaders() })
      .subscribe((data: any) => this.services = data);
  }

  createServiceType() {
    if (!this.newService.name || !this.newService.price) return;

    this.http.post('http://localhost:8000/api/services/', this.newService, { headers: this.getHeaders() })
      .subscribe({
        next: () => {
          this.fetchServices();
          // Reset form controls
          this.newService = {
            name: '',
            description: '',
            price: '',
            estimated_duration_hours: '1.0'
          };
        },
        error: (err) => console.error('Failed to register service type', err)
      });
  }

  fetchAuditLogs() {
  this.http.get('http://localhost:8000/api/admin/logs/', { headers: this.getHeaders() })
    .subscribe((data: any) => this.logs = data);
}

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}