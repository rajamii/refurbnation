import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

export const roleGuard = (allowedRoles: string[]) => {
  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);
    const user = authService.currentUser();

    if (user && allowedRoles.includes(user.role)) {
      return true;
    }
    
    router.navigate(['/login']);
    return false;
  };
};