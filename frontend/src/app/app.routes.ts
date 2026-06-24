// frontend/src/app/app.routes.ts
import { Routes } from '@angular/router';
import { roleGuard } from './services/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { 
    path: 'login', 
    loadComponent: () => import('./login/login').then(m => m.LoginComponent) 
  },
  // Protected Admin Route
  { 
    path: 'admin', 
    loadComponent: () => import('./admin/admin').then(m => m.AdminComponent),
    canActivate: [roleGuard(['ADMIN'])] 
  },
  // Protected Office Route
  { 
    path: 'office', 
    loadComponent: () => import('./office/office').then(m => m.Office),
    canActivate: [roleGuard(['OFFICE', 'ADMIN'])]
  },
  // Protected Client Route
  { 
    path: 'dashboard', 
    loadComponent: () => import('./dashboard/dashboard').then(m => m.Dashboard),
    canActivate: [roleGuard(['USER'])] 
  }
];