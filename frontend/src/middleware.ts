import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(req: NextRequest) {
  const basicAuth = req.headers.get('authorization')
  
  if (!basicAuth) {
    return new NextResponse('Authentication required', {
      status: 401,
      headers: {
        'WWW-Authenticate': 'Basic realm="Secure Area"'
      }
    })
  }

  try {
    const authValue = basicAuth.split(' ')[1]
    const [user, pwd] = atob(authValue).split(':')

    // Read from env vars, fallback to default for MVP
    const validUser = process.env.BASIC_AUTH_USER || 'admin'
    const validPwd = process.env.BASIC_AUTH_PASSWORD || 'senha123'

    if (user === validUser && pwd === validPwd) {
      return NextResponse.next()
    }
  } catch (error) {
    console.error("Basic auth parsing error", error)
  }

  return new NextResponse('Invalid credentials', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Secure Area"'
    }
  })
}

export const config = {
  // Protect all routes except static assets and Next.js internals
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
