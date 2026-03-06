# Data Model: Frontend Web Application & API Integration

## Entity Definitions

### Authentication State (Frontend)
**Description**: Runtime state representing the current authentication status of the user

**Fields**:
- `isAuthenticated`: Boolean
  - Type: Boolean
  - Constraints: Required
  - Description: Whether the user is currently authenticated

- `user`: UserObject | null
  - Type: Object (nullable)
  - Constraints: Optional
  - Description: User profile data when authenticated

- `token`: String | null
  - Type: String (nullable)
  - Constraints: Optional
  - Description: JWT token string when authenticated

- `isLoading`: Boolean
  - Type: Boolean
  - Constraints: Required
  - Description: Whether authentication state is being determined

- `error`: String | null
  - Type: String (nullable)
  - Constraints: Optional
  - Description: Any error that occurred during authentication process

**Operations**:
- `login(credentials)`: Initiates authentication process with provided credentials
- `logout()`: Clears authentication state and performs cleanup
- `refresh()`: Validates and updates current authentication state
- `isValid()`: Checks if current authentication state is valid

**Validation Rules**:
- When isAuthenticated is true, user and token should not be null
- When isAuthenticated is false, user and token should be null
- Error state should be cleared when authentication is successful

### Task Entity (Frontend Representation)
**Description**: Frontend representation of a task, mirroring backend structure

**Fields**:
- `id`: String
  - Type: String (UUID format)
  - Constraints: Required, Unique
  - Description: Unique identifier for the task

- `title`: String
  - Type: String (max 200 characters)
  - Constraints: Required, Min Length 1
  - Description: Title or headline of the task

- `description`: String | undefined
  - Type: String (optional)
  - Constraints: Optional
  - Description: Detailed description of the task

- `completed`: Boolean
  - Type: Boolean
  - Constraints: Required
  - Description: Flag indicating if the task is completed

- `createdAt`: String
  - Type: ISO Date String
  - Constraints: Required
  - Description: Timestamp when the task was created

- `updatedAt`: String
  - Type: ISO Date String
  - Constraints: Required
  - Description: Timestamp when the task was last updated

**Operations**:
- `create(taskData)`: Creates a new task with provided data
- `update(updates)`: Updates existing task with provided changes
- `delete()`: Marks task for deletion
- `toggleCompletion()`: Toggles the completed status

**Validation Rules**:
- Title must be between 1 and 200 characters
- ID must be a valid UUID format
- Completed status is either true or false
- Dates must be valid ISO date strings

### API Response Entity (Frontend)
**Description**: Structure for API responses handled by the frontend

**Fields**:
- `data`: Mixed | null
  - Type: Mixed (can be object, array, primitive)
  - Constraints: Nullable
  - Description: Actual response payload data

- `status`: Number
  - Type: HTTP Status Code
  - Constraints: Required
  - Description: HTTP status code of the response

- `statusText`: String
  - Type: String
  - Constraints: Required
  - Description: HTTP status text (e.g., "OK", "Unauthorized")

- `headers`: Object
  - Type: Key-value pairs
  - Constraints: Required
  - Description: HTTP response headers

- `error`: Object | null
  - Type: Error object (nullable)
  - Constraints: Optional
  - Description: Error information if the request failed

**Validation Rules**:
- Status must be a valid HTTP status code
- Data and error should not be populated simultaneously
- Headers must be a valid key-value object structure

### Protected Route Entity (Conceptual)
**Description**: Conceptual representation of route protection logic

**Fields**:
- `path`: String
  - Type: String (route path pattern)
  - Constraints: Required
  - Description: Path that requires authentication

- `requiresAuth`: Boolean
  - Type: Boolean
  - Constraints: Required
  - Description: Whether authentication is required to access this route

- `redirectPath`: String
  - Type: String (redirect path)
  - Constraints: Required
  - Description: Path to redirect to if authentication fails

**Operations**:
- `checkAccess()`: Validates if current user has access to route
- `protect()`: Applies protection logic to route
- `redirect()`: Redirects to appropriate path based on auth state

## Relationships

### Authentication State to Task List
- **Relationship Type**: One-to-Many (conceptual)
- **Description**: One authenticated user can have many tasks
- **Implementation**: Task list is filtered based on current user's ID
- **Constraints**:
  - Only tasks belonging to the authenticated user should be visible
  - Unauthenticated users should see empty task list
  - Task operations must include user context

### API Response to UI State
- **Relationship Type**: One-to-One
- **Description**: Each API response affects the corresponding UI state
- **Implementation**: Response data is transformed and stored in component state
- **Constraints**:
  - Successful responses update UI state appropriately
  - Error responses trigger error state handling
  - Loading states are handled during request lifecycle

## Validation Rules

### Business Logic Validation
- Users cannot access protected routes without authentication
- Task operations require valid JWT tokens
- API responses must conform to expected structures
- All form inputs must be validated before submission

### UI State Validation
- Loading states must be displayed during API requests
- Error states must show appropriate user-facing messages
- Authentication state must be consistent across all components
- Form states must reflect validation results

### Security Validation
- No sensitive information should be stored in plain text
- Authentication tokens should have appropriate security measures
- Form submissions should prevent duplicate requests
- API requests must include authentication when required

## State Transitions

### Authentication State Transitions
- **Initial State**: { isAuthenticated: false, user: null, token: null, isLoading: false, error: null }
- **Loading Transition**: Set isLoading to true while checking auth status
- **Authenticated State**: { isAuthenticated: true, user: userData, token: tokenString, isLoading: false, error: null }
- **Unauthenticated State**: { isAuthenticated: false, user: null, token: null, isLoading: false, error: errorMessage }
- **Error State**: Update error field with error message

### Task State Transitions
- **Initial State**: Empty array of tasks
- **Loading Transition**: Set loading state while fetching tasks
- **Loaded State**: Populate with tasks from API response
- **Modified State**: Update specific task in the list
- **Error State**: Show appropriate error when task operations fail

## Frontend Component States

### Loading States
- Global loading indicator during authentication checks
- Page-specific loading during data fetching
- Button loading states during form submissions
- Skeleton loaders for content placeholders

### Error States
- Global error notifications for system errors
- Form-specific error messages for validation failures
- Network error handling for API failures
- Access denied messages for authorization failures

### Success States
- Confirmation messages after successful operations
- Visual feedback for task completion toggles
- Smooth transitions after state updates
- Optimistic UI updates where appropriate