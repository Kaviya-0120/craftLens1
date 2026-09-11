import { useNavigate } from 'react-router-dom'
import { Mic, Image, Tag, IndianRupee, ShieldCheck, BookOpen, ArrowRight, CheckCircle2, Target, Users, TrendingUp, Award, Store } from 'lucide-react'
import { usePipeline } from '../context/PipelineContext'
import Card from '../components/Card'

const STEPS = [
  { to: '/voice',       num: 1, label: 'Voice',        desc: 'Record artisan description',   icon: Mic,          key: 'transcript' },
  { to: '/image',       num: 2, label: 'Image',         desc: 'Upload & process product photo', icon: Image,      key: 'imageId' },
  { to: '/listing',     num: 3, label: 'Listing',       desc: 'Generate bilingual copy',       icon: Tag,         key: 'listing' },
  { to: '/pricing',     num: 4, label: 'Pricing',       desc: 'Estimate market price',         icon: IndianRupee, key: 'pricing' },
  { to: '/consistency', num: 5, label: 'Consistency',   desc: 'Cross-modal verification',      icon: ShieldCheck, key: 'consistencyResult' },
  { to: '/catalogue',   num: 6, label: 'Publish',       desc: 'Save to catalogue',             icon: BookOpen,    key: 'publishedListingId' },
]

export default function Dashboard() {
  const { state, reset } = usePipeline()
  const navigate = useNavigate()

  return (
    <div className="bg-white">
      {/* Hero Section with Background Image */}
      <div 
        className="relative h-[50vh] md:h-[60vh] bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: 'url(/statue-bg.jpg)' }}
      >
        {/* Overlay for better text readability */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/60 to-black/80"></div>
        
        {/* Content */}
        <div className="relative h-full flex flex-col items-center justify-center text-center px-4 md:px-6">
          <h1 className="text-4xl md:text-5xl lg:text-7xl font-bold text-white mb-3 md:mb-4">
            CraftLens
          </h1>
          <p className="text-lg md:text-xl lg:text-2xl text-white/90 max-w-3xl mb-2 md:mb-3 font-light">
            Empowering Indian Artisans with AI
          </p>
          <p className="text-sm md:text-base lg:text-lg text-white/80 max-w-2xl mb-6 md:mb-10 px-4">
            Voice-first catalogue &amp; pricing assistant. Speak your craft, we handle the rest.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 md:gap-4">
            <button
              onClick={() => { reset(); navigate('/voice') }}
              className="inline-flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold px-6 md:px-10 py-3 md:py-4 rounded-lg transition-all shadow-xl hover:shadow-2xl transform hover:scale-105 text-sm md:text-base"
            >
              Start New Listing <ArrowRight className="w-4 h-4 md:w-5 md:h-5" />
            </button>
            <button
              onClick={() => navigate('/marketplace')}
              className="inline-flex items-center justify-center gap-2 bg-white hover:bg-gray-100 text-black font-semibold px-6 md:px-10 py-3 md:py-4 rounded-lg transition-all shadow-xl hover:shadow-2xl transform hover:scale-105 border-2 border-white text-sm md:text-base"
            >
              <Store className="w-4 h-4 md:w-5 md:h-5" />
              Browse Products
            </button>
          </div>
        </div>
      </div>

      {/* Tagline Section */}
      <div className="bg-gray-50 py-12 text-center border-b border-gray-200">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-bold text-black mb-4">
            Bridging Tradition with Technology
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            CraftLens is dedicated to celebrating and preserving India's rich artistic heritage 
            by connecting skilled artisans with global markets through cutting-edge AI technology.
          </p>
        </div>
      </div>

      {/* Artisan Image + Welcome Section */}
      <div className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Image */}
          <div className="order-2 lg:order-1">
            <img 
              src="/artisan-craft.jpg" 
              alt="Indian Artisan at Work" 
              className="rounded-2xl shadow-2xl w-full object-cover"
            />
          </div>
          
          {/* Content */}
          <div className="order-1 lg:order-2">
            <h2 className="text-4xl font-bold text-black mb-6">
              Welcome to CraftLens
            </h2>
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              CraftLens is a curated marketplace dedicated to celebrating the beauty of Indian 
              craftsmanship. We connect talented artisans from across the country with people who 
              appreciate authentic handmade creations.
            </p>
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              From traditional sculptures and wall murals to terracotta drinkware and handcrafted 
              decor, every piece reflects India's rich artistic heritage and the passion of skilled artisans.
            </p>
            <p className="text-lg text-gray-700 leading-relaxed">
              Our AI-powered platform simplifies the listing process, provides fair pricing guidance, 
              and ensures quality through multi-modal verification.
            </p>
          </div>
        </div>
      </div>

      {/* Impact, Target, Vision Section */}
      <div className="bg-black text-white py-16">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Our Mission */}
            <div className="text-center p-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-6">
                <Target className="w-8 h-8 text-black" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Our Target</h3>
              <p className="text-gray-300 leading-relaxed">
                Empower 10,000+ Indian artisans across rural and urban areas to digitize their 
                craft business and reach global customers with ease and dignity.
              </p>
            </div>

            {/* Impact */}
            <div className="text-center p-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-6">
                <TrendingUp className="w-8 h-8 text-black" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Our Impact</h3>
              <p className="text-gray-300 leading-relaxed">
                Increase artisan income by 40% through fair pricing, reduce listing time by 90%, 
                and preserve traditional crafts for future generations with AI assistance.
              </p>
            </div>

            {/* Recognition */}
            <div className="text-center p-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-6">
                <Award className="w-8 h-8 text-black" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Recognition</h3>
              <p className="text-gray-300 leading-relaxed">
                Supported by Open Innovation initiatives and MSJE, championing the dignity 
                of labor and economic empowerment of India's creative community.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Pipeline Progress Section */}
      <div className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-black mb-4 text-center">How It Works</h2>
        <p className="text-gray-600 text-center mb-12 max-w-2xl mx-auto">
          Our simple 6-step pipeline helps you create professional product listings in minutes
        </p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
          {STEPS.map((step, i) => {
            const done = !!state[step.key]
            const Icon = step.icon
            return (
              <Card
                key={step.num}
                className={`cursor-pointer hover:shadow-xl transition-all transform hover:-translate-y-1 border ${
                  done ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-white'
                }`}
              >
                <button className="w-full text-left" onClick={() => navigate(step.to)}>
                  <div className="flex items-start justify-between mb-3">
                    <div className={`p-3 rounded-xl ${done ? 'bg-green-200' : 'bg-gray-100'}`}>
                      <Icon className={`w-6 h-6 ${done ? 'text-green-700' : 'text-black'}`} />
                    </div>
                    {done
                      ? <CheckCircle2 className="w-6 h-6 text-green-600" />
                      : <span className="text-sm font-bold text-gray-400">STEP {step.num}</span>
                    }
                  </div>
                  <h3 className="text-lg font-bold text-black mb-2">{step.label}</h3>
                  <p className="text-sm text-gray-600">{step.desc}</p>
                </button>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Current state summary */}
      {state.fields && (
        <div className="bg-gray-50 py-12 border-t border-gray-200">
          <div className="container mx-auto px-6">
            <h2 className="text-2xl font-bold text-black mb-6 text-center">Current Session</h2>
            <Card className="shadow-lg max-w-5xl mx-auto bg-white">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-6">
                {Object.entries(state.fields).filter(([, v]) => v).map(([k, v]) => (
                  <div key={k} className="border-l-4 border-black pl-4">
                    <span className="text-xs text-gray-500 uppercase tracking-wide font-bold">
                      {k.replace(/_/g,' ')}
                    </span>
                    <p className="font-semibold text-black truncate mt-1">{String(v)}</p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Call to Action Section */}
      <div className="bg-white py-16 text-center border-t border-gray-200">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-bold text-black mb-4">
            Ready to Showcase Your Craft?
          </h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Join thousands of artisans who are already transforming their business with CraftLens
          </p>
          <button
            onClick={() => { reset(); navigate('/voice') }}
            className="inline-flex items-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold px-10 py-4 rounded-lg transition-all shadow-lg hover:shadow-xl"
          >
            Get Started Now <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
