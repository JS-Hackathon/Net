---
name: react-frontend-expert
description: Guide for writing React 19 + Vite + Tailwind for ClassManager — managing 4 roles auth, points competition data table, chart dashboard, and dynamic forms.
---

# Objective
Ensure ClassManager Frontend is written in strict TypeScript, avoids using `any`, manages UI role permissions clearly, handles loading/error states comprehensively, and aligns with the API contracts in the SRS.

---

## Instructions

### 1. Context & Project Structure Checklist
- All React files must be placed in `frontend/src/`
- Read `docs/srs/classmanager_srs_full.md` API Endpoints section before writing service calls
- Check if proxy `/api` in `vite.config.ts` points to `http://localhost:8080`
- **Component File Size Limit**: NEVER write monolithic component/page files. Keep components focused, single-purpose, and small (under 250-300 lines). Proactively extract subcomponents (such as dialogs, modals, card items, forms, filter buttons, list items) into the module's `components/` directory.

**Standard Folder Structure:**
New Frontend files must be organized in the designated directories under `frontend/src/`:
- `components/`: Contains shared UI components (`common/`, `ui/`).
- `modules/`: Contains independent modularized features (e.g., `auth/`, `dashboard/`). Each module contains `components/` (module-specific), `pages/` (completed pages), `hooks/` (module hooks), and an `index.ts` (the sole public API barrel export).
- `views/`: The router endpoints (wrappers). They import and wrap pages from `modules/` (e.g., `views/auth/Login.tsx` wraps `LoginPage` from `modules/auth`).
- `types/`: Where shared TypeScript Types/Interfaces for API objects are defined.
- `services/`: Axios API services centralized.
- `stores/`: Zustand stores for global state management.
- `contexts/`: React Context for local or session states.
- `utils/`: Utility functions (`dateUtils`, `constants`).

**Frontend Feature Development Flow:**
When developing a new frontend feature, adhere to the following sequence:
1. **Types**: Define API Response/Request interfaces in `src/types/`.
2. **Service**: Create an API service utilizing the centralized `axiosInstance` in `src/services/`.
3. **Zustand Store**: Create or update a Zustand store in `src/stores/` (e.g., `useAuthStore`) if global state sharing is required.
4. **Module components & Pages**: Build components in `src/modules/<feature>/components/` and compose them into pages in `src/modules/<feature>/pages/`. Export pages through `src/modules/<feature>/index.ts`.
5. **View Wrapper**: Create the route entry point view wrapper in `src/views/<feature>/` (e.g. `views/auth/Login.tsx` wrapping `LoginPage` from `modules/auth`).
6. **Route Guard**: Configure Route guards using `ProtectedRoute` in `App.tsx` (if authentication or specific roles are required).

### 2. Type Management (TypeScript Strict)
- DO NOT use `any` — all API data must have an `interface` or `type`
- Define types in `src/types/` by domain:

```typescript
// src/types/student.ts
export interface Student {
  id: number
  fullName: string
  googleEmail: string | null
  phoneNumber: string | null
  groupName: string
  role: 'STUDENT' | 'GROUP_LEADER'
  currentPoint: number
  approvalStatus: 'PENDING' | 'APPROVED' | 'REJECTED'
}

// src/types/pointLog.ts
export interface PointLog {
  id: number
  pointValue: number       // positive = reward, negative = penalty
  reason: string
  changedBy: string
  weekStartDate: string    // ISO date
  createdAt: string        // ISO datetime
}

// src/types/api.ts — Unified error response from BE
export interface ApiError {
  timestamp: string
  status: number
  error: string
  message: string
  details: { field: string; message: string }[]
  path: string
}

// Response for OTP send request (MVP/Testing Mode)
export interface OtpSendResponse {
  message: string
  otp?: string // Contains this code when SMS_API_KEY is empty, for direct display on UI
}
```

### 3. Environment Variables & Configuration

**Mandatory Rules:**
- DO NOT hardcode URLs or API keys in code
- All frontend environment variables must use the `VITE_` prefix to be exposed to the client
- The `.env.local` file MUST NOT be committed to Git — only commit `.env.example`

**How to read environment variables in code:**
```typescript
// ✅ CORRECT
const apiBase = import.meta.env.VITE_API_BASE_URL
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

// ❌ INCORRECT — hardcoded
const apiBase = 'http://localhost:8080'
```

**`vite.config.ts` — dev proxy to avoid CORS locally:**
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
```

**When deploying to Vercel:**
- Set `VITE_API_BASE_URL=https://your-backend.koyeb.app` in Vercel Dashboard → Settings → Environment Variables
- Set `VITE_GOOGLE_CLIENT_ID` matching Google Cloud Console

### 4. API Configuration & Zustand Store
- Use Zustand for global state management (Auth, UI states).
- Centralize all API calls in `src/services/` — DO NOT call axios directly inside components.

```typescript
// src/stores/useAuthStore.ts
import { create } from 'zustand'
import { User } from '../types/auth'

interface AuthState {
  user: User | null
  accessToken: string | null
  setUser: (user: User | null, token: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  setUser: (user, token) => set({ user, accessToken: token }),
  logout: () => set({ user: null, accessToken: null }),
}))
```

```typescript
// src/services/axiosInstance.ts
import axios from 'axios'
import { useAuthStore } from '../stores/useAuthStore'

const instance = axios.create({ baseURL: '/api/v1' })

// Request interceptor: automatically attaches Bearer token from the Zustand store
instance.interceptors.request.use(config => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor: automatically refreshes when 401
instance.interceptors.response.use(
  res => res,
  async err => {
    if (err.response?.status === 401) {
      await authService.refresh()
      return instance(err.config)
    }
    return Promise.reject(err)
  }
)
```

### 5. Role-based UI Permissions & Route Guards
- Use the Zustand store (`useAuthStore`) to verify user access privileges.
- Create a `ProtectedRoute` component to check roles before rendering.

```typescript
// src/components/common/ProtectedRoute.tsx
import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '../../stores/useAuthStore'
import { Role } from '../../types/auth'

const ProtectedRoute = ({ allowedRoles }: { allowedRoles: Role[] }) => {
  const user = useAuthStore(state => state.user)
  
  if (!user) return <Navigate to="/login" />
  if (!allowedRoles.includes(user.role)) return <Navigate to="/unauthorized" />
  return <Outlet />
}

// Use in the router (App.tsx)
<Route element={<ProtectedRoute allowedRoles={['TEACHER']} />}>
  <Route path="/dashboard" element={<DashboardPage />} />
  <Route path="/students" element={<StudentListPage />} />
</Route>
```

### 6. Color Synchronization (Tailwind & Shadcn) & Data Table
- **Minimalist Color Configuration**: To synchronize the Minimalist UI, declare the pastel color palette in [frontend/src/index.css](file:///d:/Data/Personal/JOBS/ME/class-manager/frontend/src/index.css) (CSS Variables) and configure **Shadcn / Tailwind** in `tailwind.config.js`:
  ```css
  /* src/index.css */
  :root {
    --background: 0 0% 100%;       /* Pure White #FFFFFF */
    --foreground: 20 5% 7%;        /* Charcoal #111111 */
    --card: 0 0% 98%;              /* Warm Bone #F9F9F8 */
    --border: 0 0% 92%;            /* Light Gray #EAEAEA */
    
    --pale-green: 108 20% 94%;     /* #EDF3EC */
    --pale-green-text: 125 32% 30%;/* #346538 */
    --pale-blue: 202 96% 94%;      /* #E1F3FE */
    --pale-blue-text: 204 67% 37%; /* #1F6C9F */
    --pale-yellow: 45 78% 92%;     /* #FBF3DB */
    --pale-yellow-text: 41 100% 29%;/* #956400 */
    --pale-red: 353 73% 96%;       /* #FDEBEC */
    --pale-red-text: 1 55% 40%;    /* #9F2F2D */
  }
  ```
  ```javascript
  // tailwind.config.js
  module.exports = {
    theme: {
      extend: {
        colors: {
          border: "hsl(var(--border))",
          background: "hsl(var(--background))",
          foreground: "hsl(var(--foreground))",
          card: "hsl(var(--card))",
          pale: {
            green: { DEFAULT: "hsl(var(--pale-green))", text: "hsl(var(--pale-green-text))" },
            blue: { DEFAULT: "hsl(var(--pale-blue))", text: "hsl(var(--pale-blue-text))" },
            yellow: { DEFAULT: "hsl(var(--pale-yellow))", text: "hsl(var(--pale-yellow-text))" },
            red: { DEFAULT: "hsl(var(--pale-red))", text: "hsl(var(--pale-red-text))" }
          }
        }
      }
    }
  }
  ```
- **TanStack Table**: Always include a Skeleton loading state when fetching data (do not use spinners).
- **Color Badges**: Must use the configured semantic pastel colors:

```typescript
// src/components/common/PointBadge.tsx
const getPointColor = (point: number, basePoint: number) => {
  const ratio = point / basePoint
  if (ratio >= 0.9) return 'bg-pale-green text-pale-green-text'    // Good
  if (ratio >= 0.65) return 'bg-pale-blue text-pale-blue-text'    // Fair
  if (ratio >= 0.5) return 'bg-pale-yellow text-pale-yellow-text' // Average
  return 'bg-pale-red text-pale-red-text'                         // At-risk / Weak
}
```

### 7. Dashboard Charts
- Use Recharts for weekly point charts.
- Charts must be responsive, with clear English tooltips and legends.

```typescript
// English Tooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (!active) return null
  return (
    <div className="bg-white border rounded p-2 shadow text-sm">
      <p className="font-medium">Week {label}</p>
      <p>Avg Points: <span className="font-bold">{payload[0]?.value}</span></p>
    </div>
  )
}
```

### 8. Dynamic Forms (Student Profiles)
- Render form fields from `form_template.structure` (JSONB from BE)
- Support all types: `text`, `number`, `boolean`, `select`, `date`, `textarea`
- Use React Hook Form + Zod validation

```typescript
// Dynamically render fields based on BE type
const renderField = (field: FormField) => {
  switch (field.type) {
    case 'text': return <input type="text" {...register(field.fieldName)} />
    case 'boolean': return <input type="checkbox" {...register(field.fieldName)} />
    case 'select': return (
      <select {...register(field.fieldName)}>
        {field.options?.map(opt => <option key={opt}>{opt}</option>)}
      </select>
    )
    // ... other types
  }
}
```

### 9. Loading & Error States (Mandatory)
- Every data fetch operation must support 3 states: loading / success / error
- Use Skeletons instead of spinners for tables and cards
- Error messages should use the `message` field from the BE ApiError response

```typescript
if (isLoading) return <TableSkeleton rows={10} />
if (error) return <ErrorMessage message={error.message} />
return <DataTable data={students} />
```

---

## Verification Workflow

After creating or modifying a component:

```bash
# Step 1: Navigate to frontend directory
cd frontend

# Step 2: Run linter and TypeScript check
npm run lint
npx tsc --noEmit

# Step 3: Launch the Integrated Browser to preview rendering
# Step 4: Only create the Walkthrough artifact if TypeScript compiles successfully
```

---

## Anti-patterns to Avoid

```
❌ Using `any` for data from API
❌ Calling axios/fetch directly inside components — must use services/
❌ Hardcoding role checks with raw strings ("TEACHER") — use enum/type
❌ Missing loading states when fetching data
❌ Missing handling when API fails
❌ Exposing access tokens in localStorage — use memory + HttpOnly cookie
❌ Hardcoding URLs or API keys — always use import.meta.env.VITE_*
❌ Committing .env.local to Git — only commit .env.example
❌ Using // TODO, placeholder comments — write complete implementations
❌ Using arbitrary colors for badges — only use the defined semantic colors
❌ Calling APIs in useEffect without cleanup (memory leak)
❌ Creating monolithic components (React files exceeding 300 lines) — extract subcomponents (cards, modals, forms) early

```