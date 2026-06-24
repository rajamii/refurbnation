import { inject, Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';

export interface UserProfile {
  id: number;
  email: string;
  role: 'USER' | 'OFFICE' | 'ADMIN';
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api';
  
  // Reactive State
  currentUser = signal<UserProfile | null>(null);
  token = signal<string | null>(localStorage.getItem('token'));

  login(credentials: any) {
    return this.http.post<{
      role: string; access: string, user: UserProfile 
}>(`${this.apiUrl}/token/`, credentials).pipe(
      tap(res => {
        localStorage.setItem('token', res.access);
        this.token.set(res.access);
        this.currentUser.set(res.user);
      })
    );
  }

  logout() {
    localStorage.removeItem('token');
    this.token.set(null);
    this.currentUser.set(null);
  }
}