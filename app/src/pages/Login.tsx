import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Mail, Lock, Eye, EyeOff, AlertCircle } from "lucide-react"

export default function Login() {
  const [showPassword, setShowPassword] = useState(false)
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await fetch('/react/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          identifier, 
          password 
        }),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        // Redirect to the appropriate page
        window.location.href = data.redirect
      } else {
        setError(data.error || 'Invalid email or password. Please try again.')
      }
    } catch (err) {
      setError('An error occurred during login. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-8 relative bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900">
      
      {/* Animated gradient orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-500/20 rounded-full filter blur-3xl animate-pulse" 
             style={{ animationDuration: '4s' }} />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500/20 rounded-full filter blur-3xl animate-pulse" 
             style={{ animationDuration: '6s', animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/15 rounded-full filter blur-3xl animate-pulse" 
             style={{ animationDuration: '5s', animationDelay: '2s' }} />
      </div>

      <div className="w-full max-w-[520px] relative z-10">
        {/* Title */}
        <h1 className="text-3xl font-bold text-center mb-3 text-white tracking-wide drop-shadow-lg">
          Victoria Powder Coating Ltd
        </h1>
        <p className="text-center text-gray-400 mb-6 text-sm">
          Sign in to manage production, inventory, and customer updates.
        </p>

        {/* Login Card */}
        <Card className="w-full max-w-[420px] mx-auto overflow-hidden border-white/10 shadow-2xl bg-gradient-to-br from-slate-800/95 to-slate-700/95 backdrop-blur-xl">
          <CardHeader className="border-b border-white/10 pb-6 bg-blue-600/10">
            <CardTitle className="text-xl font-bold text-white">Sign In</CardTitle>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="pt-7 pb-7 space-y-5">
              {/* Error Alert */}
              {error && (
                <Alert variant="destructive" className="bg-red-500/10 border-red-500/30 text-red-200">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Email/Username Field */}
              <div className="group">
                <div className="flex flex-col gap-3 p-4 rounded-2xl border border-white/15 bg-white/5 shadow-lg transition-all duration-150 focus-within:border-blue-400/40 focus-within:bg-white/10 focus-within:shadow-xl focus-within:shadow-blue-500/10">
                  <Label htmlFor="identifier" className="text-xs uppercase font-semibold tracking-wider text-gray-400">
                    Email or Username
                  </Label>
                  <div className="flex items-center gap-3 min-h-[24px]">
                    <Mail className="h-5 w-5 text-gray-400 flex-shrink-0" />
                    <Input
                      id="identifier"
                      type="text"
                      placeholder="Enter your email or username"
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      className="bg-transparent border-none text-white placeholder:text-gray-500 focus-visible:ring-0 focus-visible:ring-offset-0 p-0 h-auto text-base flex-1 min-h-[24px]"
                      required
                      autoFocus
                    />
                  </div>
                </div>
              </div>

              {/* Password Field */}
              <div className="group">
                <div className="flex flex-col gap-3 p-4 rounded-2xl border border-white/15 bg-white/5 shadow-lg transition-all duration-150 focus-within:border-blue-400/40 focus-within:bg-white/10 focus-within:shadow-xl focus-within:shadow-blue-500/10">
                  <Label htmlFor="password" className="text-xs uppercase font-semibold tracking-wider text-gray-400">
                    Password
                  </Label>
                  <div className="flex items-center gap-3 min-h-[24px]">
                    <Lock className="h-5 w-5 text-gray-400 flex-shrink-0" />
                    <div className="relative flex-1 min-w-0">
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="pr-10 bg-transparent border-none text-white placeholder:text-gray-500 focus-visible:ring-0 focus-visible:ring-offset-0 p-0 h-auto text-base w-full min-h-[24px]"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-0 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200 transition-colors p-1 -mr-1"
                        aria-label={showPassword ? "Hide password" : "Show password"}
                      >
                        {showPassword ? (
                          <EyeOff className="h-5 w-5" />
                        ) : (
                          <Eye className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Sign In Button */}
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-semibold text-base shadow-lg shadow-blue-600/25 hover:shadow-xl hover:shadow-blue-600/30 transition-all duration-150 hover:-translate-y-0.5"
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Signing in...
                  </div>
                ) : (
                  'Sign In'
                )}
              </Button>

              {/* Links */}
              <div className="flex flex-col gap-3 text-center -mt-1">
                <a
                  href="/customer/forgot-password"
                  className="text-sm text-blue-400 hover:text-blue-300 font-semibold hover:underline transition-colors"
                >
                  Forgot your password?
                </a>
                <Button
                  type="button"
                  variant="outline"
                  className="w-full h-12 rounded-full bg-transparent border-blue-400/40 text-blue-400 hover:bg-blue-400/10 hover:text-blue-300 font-semibold text-base transition-all duration-150"
                  onClick={() => window.location.href = '/customer/register'}
                >
                  Create Customer Account
                </Button>
              </div>
            </CardContent>
          </form>
        </Card>
      </div>
    </div>
  )
}