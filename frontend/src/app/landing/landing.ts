import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-landing',
  templateUrl: './landing.html',
  standalone: true,
  imports: [CommonModule, RouterLink]
})
export class LandingComponent {
}