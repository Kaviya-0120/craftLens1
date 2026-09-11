import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { PipelineProvider } from './context/PipelineContext'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import VoicePage from './pages/VoicePage'
import ImagePage from './pages/ImagePage'
import ListingPage from './pages/ListingPage'
import PricingPage from './pages/PricingPage'
import ConsistencyPage from './pages/ConsistencyPage'
import CataloguePage from './pages/CataloguePage'
import MarketplacePage from './pages/MarketplacePage'

export default function App() {
  return (
    <BrowserRouter>
      <PipelineProvider>
        <Routes>
          {/* Marketplace - Public facing, no Layout */}
          <Route path="/marketplace" element={<MarketplacePage />} />
          
          {/* Admin/Artisan Dashboard - With Layout */}
          <Route path="/*" element={
            <Layout>
              <Routes>
                <Route path="/"            element={<Dashboard />} />
                <Route path="/voice"       element={<VoicePage />} />
                <Route path="/image"       element={<ImagePage />} />
                <Route path="/listing"     element={<ListingPage />} />
                <Route path="/pricing"     element={<PricingPage />} />
                <Route path="/consistency" element={<ConsistencyPage />} />
                <Route path="/catalogue"   element={<CataloguePage />} />
              </Routes>
            </Layout>
          } />
        </Routes>
      </PipelineProvider>
    </BrowserRouter>
  )
}
