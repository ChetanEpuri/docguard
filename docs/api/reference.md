# API Reference

This document provides a reference for the API endpoints available in the system.

*(Note: In a fully automated setup, this page is often generated directly from `openapi.yaml` using tools like Redoc or Swagger UI).*

## Authentication
All API requests must include a Bearer token in the Authorization header.

```http
Authorization: Bearer <your_token>
```

## Endpoints

### GET /health

Retrieves the current health status of the API.

**Responses:**
- `200 OK`: Returns the status object.
- `500 Internal Server Error`: The API is experiencing issues.

**Example Request:**
```bash
curl -X GET "https://api.example.com/v1/health" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

**Example Response:**
```json
{
  "status": "ok"
}
```
