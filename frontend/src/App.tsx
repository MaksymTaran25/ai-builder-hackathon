import { useState } from 'react';
import type { ViewStage, StartupProfile, Opportunity } from './types/opportunity';
import { initialMockStartup } from './data/mockStartup';
import { mockOpportunities } from './data/mockOpportunities';
import { Navbar } from './components/Navbar';
import { Landing } from './components/Landing';
import { Intake } from './components/Intake';
import { ProfileConfirm } from './components/ProfileConfirm';
import { OpportunityMap } from './components/OpportunityMap';
import { OpportunityDetail } from './components/OpportunityDetail';
import './App.css';

function App() {
  const [viewStage, setViewStage] = useState<ViewStage>('landing');
  const [startupProfile, setStartupProfile] = useState<StartupProfile>(initialMockStartup);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);

  // Transitions
  const handleStart = () => {
    setViewStage('intake');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLoadExample = () => {
    setStartupProfile(initialMockStartup);
    setViewStage('confirm');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleAnalyze = () => {
    setViewStage('analyzing');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFinishAnalysis = () => {
    setViewStage('confirm');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleConfirmProfile = () => {
    setViewStage('map');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleEditProfile = () => {
    setViewStage('intake');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleReset = () => {
    setStartupProfile(initialMockStartup);
    setSelectedOpportunity(null);
    setViewStage('landing');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigate = (stage: ViewStage) => {
    setViewStage(stage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app-shell">
      {/* Global Navigation */}
      <Navbar
        currentStage={viewStage}
        onNavigate={handleNavigate}
        onReset={handleReset}
      />

      {/* Main Screen Content */}
      <main className="main-content">
        {viewStage === 'landing' && (
          <Landing onStart={handleStart} onLoadExample={handleLoadExample} />
        )}

        {viewStage === 'intake' && (
          <Intake
            profile={startupProfile}
            onChangeProfile={setStartupProfile}
            onSubmit={handleAnalyze}
            onLoadExample={() => setStartupProfile(initialMockStartup)}
          />
        )}

        {(viewStage === 'analyzing' || viewStage === 'confirm') && (
          <ProfileConfirm
            profile={startupProfile}
            onConfirm={handleConfirmProfile}
            onEdit={handleEditProfile}
            isAnalyzing={viewStage === 'analyzing'}
            onFinishAnalysis={handleFinishAnalysis}
          />
        )}

        {viewStage === 'map' && (
          <OpportunityMap
            opportunities={mockOpportunities}
            startupProfile={startupProfile}
            onExploreOpportunity={(opp) => setSelectedOpportunity(opp)}
            onEditProfile={handleEditProfile}
          />
        )}
      </main>

      {/* Detail Modal / Panel */}
      {selectedOpportunity && (
        <OpportunityDetail
          opportunity={selectedOpportunity}
          onClose={() => setSelectedOpportunity(null)}
        />
      )}

      {/* App Footer */}
      <footer className="site-footer">
        <div className="footer-inner">
          <div className="footer-brand-info">
            <strong>Government Opportunity Map</strong>
            <span>Built for the 2026 AI Builder Hackathon • Independent Founder Edition</span>
          </div>
          <div className="footer-links">
            <span className="footer-pill">NSF • NIH • ARPA-H • VA • ONC • DoD</span>
            <span className="footer-disclaimer">
              Powered by public federal data and award records. For advisory and planning use.
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
