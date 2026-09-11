import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Filter, Phone, Mail, MapPin, Package, Tag as TagIcon, Home, Sparkles, MessageCircle } from 'lucide-react'
import Card from '../components/Card'

// Mock data for demonstration - Replace with API call
const MOCK_PRODUCTS = [
  {
    id: 'listing_001',
    image_url: 'https://img.freepik.com/premium-photo/handcrafted-wooden-bowl-showcasing-natural-texture-warmth-timeless-kitchen-setting-transparent-png-background_94628-98005.jpg',
    title_english: 'Handcrafted Clay Pottery Bowl',
    description_english: 'Beautiful handcrafted pottery bowl made from natural clay. Perfect for serving traditional Indian dishes. Each piece is unique and crafted with care by skilled artisans.',
    price_min: 450,
    price_max: 650,
    price: 550,
    artisan_name: 'Ramesh Kumar',
    artisan_region: 'Khurja, Uttar Pradesh',
    artisan_phone: '+919876543210',
    artisan_whatsapp: '+919876543210',
    artisan_email: 'ramesh.pottery@email.com',
    craft_type: 'Pottery',
    material: 'Clay',
    material_origin: 'Naturally sourced from the banks of the Ganges River. This clay is known for its purity and has been used for centuries in traditional pottery making.',
    experience_years: 15,
    size: 'Medium (8 inches diameter)',
    color: 'Terracotta Brown'
  },
  {
    id: 'listing_002',
    image_url: '/statue-bg.jpg',
    title_english: 'Traditional Brass Sculpture',
    description_english: 'Exquisite brass sculpture depicting traditional Indian deity. Handcrafted using ancient techniques passed down through generations. Perfect for home temples and spiritual spaces.',
    price_min: 2500,
    price_max: 3500,
    price: 3000,
    artisan_name: 'Lakshmi Devi',
    artisan_region: 'Thanjavur, Tamil Nadu',
    artisan_phone: '+919765432109',
    artisan_whatsapp: '+919765432109',
    artisan_email: 'lakshmi.brass@email.com',
    craft_type: 'Metal Work',
    material: 'Brass',
    material_origin: 'Premium quality brass alloy, naturally composed of copper and zinc. Sourced from traditional foundries in South India, known for producing the finest brass for religious artifacts.',
    experience_years: 20,
    size: 'Large (12 inches height)',
    color: 'Golden Brass'
  },
  {
    id: 'listing_003',
    image_url: 'https://i.pinimg.com/736x/39/69/bb/3969bbc7958a4b8fee3c56dbe89e96f7.jpg',
    title_english: 'Wooden Wall Hanging Art',
    description_english: 'Intricate wooden wall art featuring traditional patterns. Carved by hand from sustainable wood. Adds warmth and cultural elegance to any space.',
    price_min: 1200,
    price_max: 1800,
    price: 1500,
    artisan_name: 'Suresh Rao',
    artisan_region: 'Saharanpur, Uttar Pradesh',
    artisan_phone: '+919654321098',
    artisan_whatsapp: '+919654321098',
    artisan_email: 'suresh.wood@email.com',
    craft_type: 'Wood Carving',
    material: 'Sheesham Wood',
    material_origin: 'Naturally grown Sheesham (Indian Rosewood) from sustainable forests in North India. This hardwood is prized for its durability, rich grain patterns, and resistance to decay.',
    experience_years: 12,
    size: 'Medium (18x12 inches)',
    color: 'Natural Wood Finish'
  },
  {
    id: 'listing_004',
    image_url: 'https://tse1.explicit.bing.net/th/id/OIP.bSPf5zIWTzf0_hIT3a3H_AHaJ4?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
    title_english: 'Handloom Silk Saree with Zari Border',
    description_english: 'Exquisite handloom silk saree with traditional zari border. Woven by skilled artisans using pure silk threads. Perfect for weddings and festive occasions.',
    price_min: 4500,
    price_max: 6500,
    price: 5500,
    artisan_name: 'Kamala Bai',
    artisan_region: 'Kanchipuram, Tamil Nadu',
    artisan_phone: '+919543210987',
    artisan_whatsapp: '+919543210987',
    artisan_email: 'kamala.saree@email.com',
    craft_type: 'Handloom Weaving',
    material: 'Pure Silk',
    material_origin: 'Naturally sourced pure mulberry silk from traditional sericulture farms in South India. The silk threads are extracted from silk cocoons and hand-spun to maintain their natural luster and strength. Zari threads are made from pure silver coated with gold.',
    experience_years: 25,
    size: '6.5 yards with blouse piece',
    color: 'Traditional Red with Golden Zari'
  },
  {
    id: 'listing_005',
    image_url: 'https://i.etsystatic.com/28421345/r/il/9d939c/3159499066/il_fullxfull.3159499066_hbf8.jpg',
    title_english: 'Handcrafted Wooden Wall Hanging',
    description_english: 'Beautiful wooden wall hanging with intricate carved designs. Features traditional Indian motifs and patterns. Perfect statement piece for living rooms and offices.',
    price_min: 2200,
    price_max: 3200,
    price: 2700,
    artisan_name: 'Vijay Kumar',
    artisan_region: 'Jaipur, Rajasthan',
    artisan_phone: '+919432109876',
    artisan_whatsapp: '+919432109876',
    artisan_email: 'vijay.carving@email.com',
    craft_type: 'Wood Carving',
    material: 'Mango Wood',
    material_origin: 'Naturally sourced mango wood from sustainable orchards in Rajasthan. After mango trees stop bearing fruit, the wood is harvested and seasoned for crafting. This eco-friendly practice gives new life to old trees while producing beautiful, durable wood with unique grain patterns.',
    experience_years: 18,
    size: 'Large (24x18 inches)',
    color: 'Dark Walnut Finish'
  }
]

export default function MarketplacePage() {
  const navigate = useNavigate()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedProduct, setSelectedProduct] = useState(null)

  useEffect(() => {
    // Load products from localStorage (published listings) and merge with mock data
    const loadProducts = () => {
      try {
        const publishedListings = JSON.parse(localStorage.getItem('publishedListings') || '[]')
        const allProducts = [...publishedListings, ...MOCK_PRODUCTS]
        setProducts(allProducts)
      } catch (e) {
        console.error('Error loading products:', e)
        setProducts(MOCK_PRODUCTS)
      }
      setLoading(false)
    }

    // Simulate API call
    setTimeout(loadProducts, 500)
  }, [])

  const filteredProducts = products.filter(p => 
    searchQuery === '' ||
    p.title_english.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.artisan_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.craft_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.material.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="bg-white min-h-screen">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo/Brand */}
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
              <Sparkles className="w-6 h-6 text-black" />
              <span className="text-xl font-bold tracking-tight text-black">CraftLens</span>
              <span className="text-sm text-gray-500 ml-2">Marketplace</span>
            </div>
            
            {/* Navigation */}
            <nav className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg text-sm font-medium transition-colors"
              >
                <Home className="w-4 h-4" />
                Artisan Portal
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="bg-gradient-to-b from-gray-900 to-gray-800 text-white py-16">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            CraftLens Marketplace
          </h1>
          <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto mb-8">
            Discover authentic handcrafted products from talented Indian artisans
          </p>
          
          {/* Search Bar */}
          <div className="max-w-2xl mx-auto relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by product, artisan, craft type, or material..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 rounded-lg bg-white text-gray-900 text-base placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-white shadow-lg"
            />
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="container mx-auto px-6 py-12">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold text-black">
            Featured Products ({filteredProducts.length})
          </h2>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium">
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>

        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block w-8 h-8 border-4 border-gray-300 border-t-black rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-600">Loading products...</p>
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="text-center py-20">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">No products found matching your search.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProducts.map((product) => (
              <Card 
                key={product.id}
                className="hover:shadow-xl transition-all transform hover:-translate-y-1"
              >
                {/* Product Image */}
                <div className="w-full h-48 bg-gray-100 rounded-xl mb-4 overflow-hidden">
                  <img
                    src={product.image_url}
                    alt={product.title_english}
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Product Info */}
                <h3 className="font-bold text-lg text-black mb-3 line-clamp-2">
                  {product.title_english}
                </h3>
                
                <p className="text-sm text-gray-700 mb-4 line-clamp-3">
                  {product.description_english}
                </p>

                {/* Price */}
                <div className="mb-4 pb-4 border-b border-gray-200">
                  <span className="text-2xl font-bold text-black">
                    ₹{product.price.toLocaleString('en-IN')}
                  </span>
                  {product.price_min && product.price_max && (
                    <p className="text-xs text-gray-500 mt-1">
                      Range: ₹{product.price_min.toLocaleString('en-IN')} - ₹{product.price_max.toLocaleString('en-IN')}
                    </p>
                  )}
                </div>

                {/* Artisan Info Preview */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-xs font-bold text-gray-600">
                        {product.artisan_name.charAt(0)}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-black truncate">{product.artisan_name}</p>
                      <p className="text-xs text-gray-500 truncate">{product.artisan_region}</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                      {product.craft_type}
                    </span>
                    <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                      {product.material}
                    </span>
                  </div>
                </div>

                <button 
                  onClick={() => setSelectedProduct(product)}
                  className="w-full mt-4 bg-black text-white font-semibold py-2 rounded-lg hover:bg-gray-800 transition-colors text-sm"
                >
                  View Details
                </button>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-50 overflow-y-auto"
          onClick={() => setSelectedProduct(null)}
        >
          <div className="min-h-screen px-4 py-8 flex items-center justify-center">
            <div 
              className="bg-white rounded-2xl max-w-4xl w-full shadow-2xl overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="grid grid-cols-1 md:grid-cols-2">
                {/* Left: Image */}
                <div className="bg-gray-100 p-8 flex items-center justify-center">
                  <img
                    src={selectedProduct.image_url}
                    alt={selectedProduct.title_english}
                    className="max-w-full max-h-96 object-contain rounded-lg"
                  />
                </div>

                {/* Right: Details */}
                <div className="p-8 overflow-y-auto max-h-[600px]">
                  <button
                    onClick={() => setSelectedProduct(null)}
                    className="float-right text-gray-400 hover:text-black text-2xl leading-none"
                  >
                    ×
                  </button>

                  <h2 className="text-2xl font-bold text-black mb-6">
                    {selectedProduct.title_english}
                  </h2>

                  {/* Price */}
                  <div className="mb-6 pb-6 border-b border-gray-200">
                    <div className="flex items-baseline gap-2 mb-2">
                      <span className="text-3xl font-bold text-black">
                        ₹{selectedProduct.price.toLocaleString('en-IN')}
                      </span>
                      <span className="text-sm text-gray-500">
                        (Market-based)
                      </span>
                    </div>
                    {selectedProduct.price_min && selectedProduct.price_max && (
                      <p className="text-sm text-gray-600">
                        Price Range: ₹{selectedProduct.price_min.toLocaleString('en-IN')} - ₹{selectedProduct.price_max.toLocaleString('en-IN')}
                      </p>
                    )}
                  </div>

                  {/* Description */}
                  <div className="mb-6">
                    <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-2">
                      Product Description
                    </h3>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {selectedProduct.description_english}
                    </p>
                  </div>

                  {/* Product Details */}
                  <div className="mb-6">
                    <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-3">
                      Product Details
                    </h3>
                    <div className="grid grid-cols-2 gap-3 mb-4">
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs text-gray-500 mb-1">Craft Type</p>
                        <p className="text-sm font-semibold text-black">{selectedProduct.craft_type}</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs text-gray-500 mb-1">Material</p>
                        <p className="text-sm font-semibold text-black">{selectedProduct.material}</p>
                      </div>
                      {selectedProduct.size && (
                        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                          <p className="text-xs text-gray-500 mb-1">Size</p>
                          <p className="text-sm font-semibold text-black">{selectedProduct.size}</p>
                        </div>
                      )}
                      {selectedProduct.color && (
                        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                          <p className="text-xs text-gray-500 mb-1">Color</p>
                          <p className="text-sm font-semibold text-black">{selectedProduct.color}</p>
                        </div>
                      )}
                    </div>
                    
                    {/* Material Origin */}
                    {selectedProduct.material_origin && (
                      <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-4 border border-gray-200">
                        <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wide mb-2 flex items-center gap-2">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
                          Natural Material Source
                        </h4>
                        <p className="text-sm text-gray-700 leading-relaxed">
                          {selectedProduct.material_origin}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Artisan Information */}
                  <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                    <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-4">
                      Artisan Information
                    </h3>
                    
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-black rounded-full flex items-center justify-center">
                          <span className="text-white font-bold text-lg">
                            {selectedProduct.artisan_name.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <p className="font-bold text-black">{selectedProduct.artisan_name}</p>
                          <p className="text-xs text-gray-500">
                            {selectedProduct.experience_years}+ years of experience
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start gap-2 text-sm">
                        <MapPin className="w-4 h-4 text-gray-500 mt-0.5 shrink-0" />
                        <span className="text-gray-700">{selectedProduct.artisan_region}</span>
                      </div>

                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="w-4 h-4 text-gray-500 shrink-0" />
                        <a 
                          href={`tel:${selectedProduct.artisan_phone}`}
                          className="text-gray-700 hover:text-black font-medium"
                        >
                          {selectedProduct.artisan_phone}
                        </a>
                      </div>
                      
                      {selectedProduct.artisan_whatsapp && (
                        <div className="flex items-center gap-2 text-sm">
                          <MessageCircle className="w-4 h-4 text-gray-500 shrink-0" />
                          <a 
                            href={`https://wa.me/${selectedProduct.artisan_whatsapp.replace(/\D/g, '')}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-700 hover:text-black font-medium"
                          >
                            Chat on WhatsApp
                          </a>
                        </div>
                      )}

                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="w-4 h-4 text-gray-500 shrink-0" />
                        <a 
                          href={`mailto:${selectedProduct.artisan_email}`}
                          className="text-gray-700 hover:text-black font-medium truncate"
                        >
                          {selectedProduct.artisan_email}
                        </a>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-2 gap-3">
                      <a
                        href={`tel:${selectedProduct.artisan_phone}`}
                        className="flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold py-3 rounded-lg text-center transition-colors"
                      >
                        <Phone className="w-4 h-4" />
                        Call
                      </a>
                      {selectedProduct.artisan_whatsapp && (
                        <a
                          href={`https://wa.me/${selectedProduct.artisan_whatsapp.replace(/\D/g, '')}?text=Hi, I'm interested in your ${selectedProduct.title_english}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg text-center transition-colors"
                        >
                          <MessageCircle className="w-4 h-4" />
                          WhatsApp
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Footer */}
      <footer className="bg-black text-gray-400 py-8 mt-16">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-6">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-white" />
                <span className="text-lg font-bold text-white">CraftLens</span>
              </div>
              <p className="text-sm text-gray-400">
                Empowering Indian artisans through AI-powered catalogue and pricing solutions.
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-3">Quick Links</h4>
              <ul className="space-y-2 text-sm">
                <li><button onClick={() => navigate('/')} className="hover:text-white transition-colors">Artisan Portal</button></li>
                <li><button onClick={() => setSearchQuery('')} className="hover:text-white transition-colors">All Products</button></li>
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-3">Support</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Contact Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms & Conditions</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-700 pt-6 text-center">
            <p className="text-sm">© 2026 CraftLens - Celebrating Indian Craftsmanship</p>
            <p className="text-xs mt-2">Open Innovation · MSJE</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
