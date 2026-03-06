/**
 * Test script to verify JWT token decoding
 * This demonstrates how the API client extracts user_id from JWT
 */

function testJWTDecode() {
  // Example JWT token from FastAPI backend
  // Payload: {"sub": "123e4567-e89b-12d3-a456-426614174000", "exp": 1234567890}
  const exampleToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJleHAiOjE3MzkyMzI4MDB9.xxxxx";

  // Decode JWT (same logic as api-client.ts)
  const parts = exampleToken.split('.');
  if (parts.length !== 3) {
    console.error('Invalid JWT format');
    return;
  }

  // Decode the payload (base64url)
  const payload = parts[1];
  const decodedPayload = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
  const parsedPayload = JSON.parse(decodedPayload);

  console.log('Decoded JWT Payload:', parsedPayload);
  console.log('User ID (sub):', parsedPayload.sub);
  console.log('Expiry (exp):', new Date(parsedPayload.exp * 1000).toISOString());
}

// Run the test
if (typeof window !== 'undefined') {
  console.log('=== JWT Decode Test ===');
  testJWTDecode();
}

export {};
