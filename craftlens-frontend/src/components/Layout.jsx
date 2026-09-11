import { NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import {
  Mic, Image, Tag, IndianRupee, ShieldCheck, BookOpen, Sparkles, UserCircle, X, Store, Hammer, ShoppingBag,
} from 'lucide-react'

const NAV = [
  { to: '/',           label: 'Home' },
  { to: '/voice',      label: 'Voice' },
  { to: '/image',      label: 'Image' },
  { to: '/listing',    label: 'Listing' },
  { to: '/pricing',    label: 'Pricing' },
  { to: '/consistency',label: 'Consistency' },
  { to: '/catalogue',  label: 'Publish' },
]

export default function Layout({ children }) {
  const navigate = useNavigate()
  const [showArtisanModal, setShowArtisanModal] = useState(false)
  const [showCustomerModal, setShowCustomerModal] = useState(false)
  const [artisanFormData, setArtisanFormData] = useState({
    name: '',
    craftType: '',
    region: '',
    experience: '',
    phone: '',
    email: '',
  })
  const [customerFormData, setCustomerFormData] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
    interest: '',
  })

  const handleArtisanSubmit = (e) => {
    e.preventDefault()
    
    // Save artisan info to localStorage
    localStorage.setItem('artisanProfile', JSON.stringify({
      name: artisanFormData.name,
      craftType: artisanFormData.craftType,
      region: artisanFormData.region,
      experience: artisanFormData.experience,
      phone: artisanFormData.phone,
      email: artisanFormData.email || `${artisanFormData.phone}@artisan.com`,
      whatsapp: artisanFormData.phone,
      userType: 'artisan',
    }))
    
    alert('Welcome, ' + artisanFormData.name + '! You can now create listings.')
    setShowArtisanModal(false)
    setArtisanFormData({ name: '', craftType: '', region: '', experience: '', phone: '', email: '' })
  }

  const handleCustomerSubmit = (e) => {
    e.preventDefault()
    
    // Save customer info to localStorage
    localStorage.setItem('customerProfile', JSON.stringify({
      name: customerFormData.name,
      email: customerFormData.email,
      phone: customerFormData.phone,
      location: customerFormData.location,
      interest: customerFormData.interest,
      userType: 'customer',
    }))
    
    alert('Welcome, ' + customerFormData.name + '! Redirecting to marketplace...')
    setShowCustomerModal(false)
    setCustomerFormData({ name: '', email: '', phone: '', location: '', interest: '' })
    // Redirect to marketplace
    navigate('/marketplace')
  }

  return (
    <div className="min-h-screen flex flex-col bg-white font-sans">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-3 md:px-6">
          <div className="flex items-center justify-between h-14 md:h-16">
            {/* Logo/Brand */}
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 md:w-6 md:h-6 text-black" />
              <span className="text-lg md:text-xl font-bold tracking-tight text-black">CraftLens</span>
            </div>
            
            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-1">
              {NAV.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-black text-white'
                        : 'text-gray-700 hover:bg-gray-100 hover:text-black'
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
              
              {/* Marketplace Button */}
              <button
                onClick={() => navigate('/marketplace')}
                className="ml-2 flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
              >
                <Store className="w-4 h-4" />
                Marketplace
              </button>
              
              {/* Artisan Login Button */}
              <button
                onClick={() => setShowArtisanModal(true)}
                className="ml-2 flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
              >
                <Hammer className="w-4 h-4" />
                Artisan
              </button>
              
              {/* Customer Login Button */}
              <button
                onClick={() => setShowCustomerModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-white text-black border-2 border-black rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                <ShoppingBag className="w-4 h-4" />
                Customer
              </button>
            </nav>

            {/* Mobile Navigation - Simplified */}
            <div className="flex lg:hidden items-center gap-2">
              <button
                onClick={() => navigate('/marketplace')}
                className="p-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Store className="w-5 h-5" />
              </button>
              
              <button
                onClick={() => setShowArtisanModal(true)}
                className="p-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
              >
                <Hammer className="w-5 h-5" />
              </button>
              
              <button
                onClick={() => setShowCustomerModal(true)}
                className="p-2 bg-white text-black border-2 border-black rounded-lg hover:bg-gray-50 transition-colors"
              >
                <ShoppingBag className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="bg-black text-gray-400 py-6 text-center">
        <div className="container mx-auto px-6">
          <p className="text-sm">© 2026 CraftLens - Empowering Indian Artisans</p>
          <p className="text-xs mt-2">Open Innovation · MSJE</p>
        </div>
      </footer>

      {/* Artisan Login Modal */}
      {showArtisanModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative">
            <button
              onClick={() => setShowArtisanModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X className="w-6 h-6" />
            </button>
            
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-black rounded-full flex items-center justify-center">
                <Hammer className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-black">Artisan Login</h2>
                <p className="text-gray-600 text-sm">Create and manage your product listings</p>
              </div>
            </div>
            
            <form onSubmit={handleArtisanSubmit} className="space-y-4 mt-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  value={artisanFormData.name}
                  onChange={(e) => setArtisanFormData({ ...artisanFormData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="Enter your name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Craft Type *
                </label>
                <input
                  type="text"
                  required
                  value={artisanFormData.craftType}
                  onChange={(e) => setArtisanFormData({ ...artisanFormData, craftType: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="e.g., Pottery, Weaving, Wood carving"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Region/State *
                </label>
                <input
                  type="text"
                  required
                  value={artisanFormData.region}
                  onChange={(e) => setArtisanFormData({ ...artisanFormData, region: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="Your city or state"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Years of Experience
                </label>
                <input
                  type="number"
                  value={artisanFormData.experience}
                  onChange={(e) => setArtisanFormData({ ...artisanFormData, experience: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="Years"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  required
                  value={artisanFormData.phone}
                  onChange={(e) => setArtisanFormData({ ...artisanFormData, phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="+91 XXXXX XXXXX"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={artisanFormData.email}
                  onChange={(e) => setArtisanFormData({ ...artisanFormData, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="your.email@example.com"
                />
              </div>
              
              <button
                type="submit"
                className="w-full bg-black text-white font-semibold py-3 rounded-lg hover:bg-gray-800 transition-colors mt-6"
              >
                Register as Artisan
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Customer Login Modal */}
      {showCustomerModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative">
            <button
              onClick={() => setShowCustomerModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X className="w-6 h-6" />
            </button>
            
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-black rounded-full flex items-center justify-center">
                <ShoppingBag className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-black">Customer Login</h2>
                <p className="text-gray-600 text-sm">Browse and purchase authentic handcrafted products</p>
              </div>
            </div>
            
            <form onSubmit={handleCustomerSubmit} className="space-y-4 mt-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  value={customerFormData.name}
                  onChange={(e) => setCustomerFormData({ ...customerFormData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="Enter your name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Email Address *
                </label>
                <input
                  type="email"
                  required
                  value={customerFormData.email}
                  onChange={(e) => setCustomerFormData({ ...customerFormData, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="your.email@example.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  required
                  value={customerFormData.phone}
                  onChange={(e) => setCustomerFormData({ ...customerFormData, phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="+91 XXXXX XXXXX"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  value={customerFormData.location}
                  onChange={(e) => setCustomerFormData({ ...customerFormData, location: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                  placeholder="Your city or state"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Interest in Crafts
                </label>
                <select
                  value={customerFormData.interest}
                  onChange={(e) => setCustomerFormData({ ...customerFormData, interest: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none"
                >
                  <option value="">Select your interest</option>
                  <option value="Pottery">Pottery</option>
                  <option value="Wood Carving">Wood Carving</option>
                  <option value="Metal Work">Metal Work</option>
                  <option value="Textiles">Textiles & Sarees</option>
                  <option value="Paintings">Paintings</option>
                  <option value="Jewelry">Jewelry</option>
                  <option value="Home Decor">Home Decor</option>
                  <option value="All">All Crafts</option>
                </select>
              </div>
              
              <button
                type="submit"
                className="w-full bg-black text-white font-semibold py-3 rounded-lg hover:bg-gray-800 transition-colors mt-6"
              >
                Continue to Marketplace
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
