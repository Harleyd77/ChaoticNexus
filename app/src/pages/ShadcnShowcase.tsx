import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { useToast } from "@/hooks/use-toast"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Switch } from "@/components/ui/switch"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { AlertCircle, CheckCircle2, Info, Palette, Users, Briefcase } from "lucide-react"

export default function ShadcnShowcase() {
  const { toast } = useToast()

  const sampleJobs = [
    { id: "47", company: "Acme Railings", status: "In Progress", color: "RAL 9005", dueDate: "2025-10-01" },
    { id: "48", company: "Island Fabricators", status: "Pending", color: "RAL 7016", dueDate: "2025-09-30" },
    { id: "49", company: "Westbay Marine", status: "Completed", color: "Clear Coat", dueDate: "2025-09-28" },
  ]

  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight">Shadcn/ui Showcase</h1>
        <p className="text-muted-foreground mt-2">
          Complete component library integrated with your PowderApp
        </p>
      </div>

      {/* Alerts Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Alerts & Notifications</h2>
        <div className="grid gap-4">
          <Alert>
            <Info className="h-4 w-4" />
            <AlertTitle>Information</AlertTitle>
            <AlertDescription>
              Your job intake form has been successfully submitted.
            </AlertDescription>
          </Alert>

          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              Unable to process powder color. Please check the RAL code.
            </AlertDescription>
          </Alert>
        </div>
      </section>

      {/* Buttons Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Buttons</h2>
        <div className="flex flex-wrap gap-4">
          <Button>Default</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
          <Button onClick={() => toast({ title: "Success!", description: "Job saved successfully" })}>
            Show Toast
          </Button>
        </div>

        <div className="flex flex-wrap gap-4">
          <Button size="sm">Small</Button>
          <Button size="default">Default</Button>
          <Button size="lg">Large</Button>
          <Button size="icon">
            <Palette className="h-4 w-4" />
          </Button>
        </div>
      </section>

      {/* Cards & Stats */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Cards & Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Jobs</CardTitle>
              <Briefcase className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-muted-foreground">+3 from last week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">156</div>
              <p className="text-xs text-muted-foreground">+8 this month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Powder Colors</CardTitle>
              <Palette className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">89</div>
              <p className="text-xs text-muted-foreground">Available in stock</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Form Elements */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Form Elements</h2>
        <Card>
          <CardHeader>
            <CardTitle>New Job Intake</CardTitle>
            <CardDescription>Create a new production job with powder coating specifications</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="customer">Customer Name</Label>
                <Input id="customer" placeholder="Enter customer name" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="color">Powder Color</Label>
                <Select>
                  <SelectTrigger id="color">
                    <SelectValue placeholder="Select color" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ral9005">RAL 9005 - Jet Black</SelectItem>
                    <SelectItem value="ral7016">RAL 7016 - Anthracite Grey</SelectItem>
                    <SelectItem value="ral3000">RAL 3000 - Flame Red</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Job Options</Label>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Checkbox id="rush" />
                  <label htmlFor="rush" className="text-sm font-medium">
                    Rush Order
                  </label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="priority" />
                  <label htmlFor="priority" className="text-sm font-medium">
                    High Priority
                  </label>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Switch id="notify" />
                <Label htmlFor="notify">Send notifications</Label>
              </div>
              <Badge>Standard</Badge>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label>Progress</Label>
              <Progress value={66} className="w-full" />
              <p className="text-xs text-muted-foreground">66% complete</p>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline">Cancel</Button>
            <Button>Submit Job</Button>
          </CardFooter>
        </Card>
      </section>

      {/* Table Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Data Tables</h2>
        <Card>
          <CardHeader>
            <CardTitle>Recent Jobs</CardTitle>
            <CardDescription>A list of your recent production jobs</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableCaption>Recent production jobs for powder coating</TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">Job ID</TableHead>
                  <TableHead>Company</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Color</TableHead>
                  <TableHead className="text-right">Due Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sampleJobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell className="font-medium">#{job.id}</TableCell>
                    <TableCell>{job.company}</TableCell>
                    <TableCell>
                      <Badge variant={job.status === "Completed" ? "default" : "secondary"}>
                        {job.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{job.color}</TableCell>
                    <TableCell className="text-right">{job.dueDate}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </section>

      {/* Tabs Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Tabs & Navigation</h2>
        <Tabs defaultValue="jobs" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="jobs">Jobs</TabsTrigger>
            <TabsTrigger value="customers">Customers</TabsTrigger>
            <TabsTrigger value="powders">Powders</TabsTrigger>
          </TabsList>
          <TabsContent value="jobs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Job Management</CardTitle>
                <CardDescription>Manage your production jobs and work orders</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  View, edit, and track all your powder coating jobs in one place.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="customers" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Customer Management</CardTitle>
                <CardDescription>Manage customer information and contacts</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Store and manage all your customer data efficiently.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="powders" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Powder Inventory</CardTitle>
                <CardDescription>Track your powder coating colors and stock</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Monitor powder levels and manage your color inventory.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </section>

      {/* Dialog Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Dialogs & Modals</h2>
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="outline">Open Dialog</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Edit Job Details</DialogTitle>
              <DialogDescription>
                Make changes to your job details here. Click save when you're done.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="name" className="text-right">
                  Name
                </Label>
                <Input id="name" value="Acme Railings" className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="color" className="text-right">
                  Color
                </Label>
                <Input id="color" value="RAL 9005" className="col-span-3" />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit">Save changes</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </section>

      {/* Avatars Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Avatars & Users</h2>
        <div className="flex gap-4">
          <Avatar>
            <AvatarImage src="https://github.com/shadcn.png" alt="User" />
            <AvatarFallback>CN</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarFallback>JD</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarFallback>AB</AvatarFallback>
          </Avatar>
        </div>
      </section>
    </div>
  )
}
