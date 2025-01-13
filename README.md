# Flask Car Rental System

A Flask-based Car Rental System with role-based access control for Admin and User functionalities. The system uses a database (e.g., SQLite) for data management and implements user authentication with Flask-Login. The application separates admin and user pages to ensure secure and proper access control.

---

## Features

### Admin Endpoints:
1. **View All Cars**  
   - **Endpoint:** `GET /admin/cars`  
   - **Description:** Allows admins to view a list of all cars in the system.

2. **Add a New Car**  
   - **Endpoint:** `POST /admin/cars`  
   - **Description:** Enables admins to add a new car to the system.

3. **Update Car Details**  
   - **Endpoint:** `PUT /admin/cars/<car_id>`  
   - **Description:** Allows admins to update details of a specific car by its `car_id`.

4. **Delete a Car**  
   - **Endpoint:** `DELETE /admin/cars/<car_id>`  
   - **Description:** Allows admins to delete a specific car by its `car_id`.

### User Endpoints:
1. **View Available Cars**  
   - **Endpoint:** `GET /cars`  
   - **Description:** Allows users to view a list of cars available for rent.

2. **Rent a Car**  
   - **Endpoint:** `POST /cars/rent`  
   - **Description:** Enables users to rent a car.

3. **Return a Car**  
   - **Endpoint:** `POST /cars/return`  
   - **Description:** Allows users to return a rented car.

---
