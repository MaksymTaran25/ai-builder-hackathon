import React from 'react';
import {
  IconArrowRight,
  IconShieldCheck,
  IconSparkles,
  IconLandmark,
  IconDollarSign,
  IconAward,
  IconCheckCircle2,
  IconBuilding,
  IconTrendingUp,
} from './icons';

interface LandingProps {
  onStart: () => void;
  onLoadExample: () => void;
}

export const Landing: React.FC<LandingProps> = ({ onStart, onLoadExample }) => {
  return (
    <div className="landing-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="trust-pill-hero">
          <IconShieldCheck size={16} />
          <span>Powered by public federal data & historical award records</span>
        </div>

        <h1 className="hero-headline">
          Turn government bureaucracy into startup opportunity.
        </h1>

        <p className="hero-subheadline">
          Tell us about your company. We’ll find the federal programs, funding opportunities,
          and government resources that could help you grow.
        </p>

        <div className="hero-cta-group">
          <button type="button" className="btn-primary-lg" onClick={onStart} id="discover-btn">
            <span>Discover opportunities</span>
            <IconArrowRight size={20} />
          </button>

          <button
            type="button"
            className="btn-secondary-lg"
            onClick={onLoadExample}
            id="quick-demo-btn"
          >
            <IconSparkles size={18} />
            <span>Try with Hackathon Demo Startup</span>
          </button>
        </div>

        <div className="founder-guarantee-note">
          <IconCheckCircle2 size={14} />
          <span>100% Non-dilutive capital discovery • No equity forfeited • No government jargon</span>
        </div>

        {/* Visual Process Flow */}
        <div className="visual-flow-card">
          <div className="flow-step">
            <div className="flow-badge">Step 1</div>
            <div className="flow-icon-wrap">
              <IconBuilding size={24} />
            </div>
            <div className="flow-text-group">
              <div className="flow-title">YOUR STARTUP</div>
              <div className="flow-desc">Describe your tech, product stage, and capital need in plain language.</div>
            </div>
          </div>

          <div className="flow-divider">
            <IconArrowRight size={20} className="flow-arrow" />
          </div>

          <div className="flow-step highlight">
            <div className="flow-badge intelligence">Step 2</div>
            <div className="flow-icon-wrap intelligence">
              <IconSparkles size={24} />
            </div>
            <div className="flow-text-group">
              <div className="flow-title">GOVERNMENT INTELLIGENCE</div>
              <div className="flow-desc">Synthesizes SBIR/STTR, agency solicitations, and past award winners.</div>
            </div>
          </div>

          <div className="flow-divider">
            <IconArrowRight size={20} className="flow-arrow" />
          </div>

          <div className="flow-step">
            <div className="flow-badge">Step 3</div>
            <div className="flow-icon-wrap">
              <IconAward size={24} />
            </div>
            <div className="flow-text-group">
              <div className="flow-title">OPPORTUNITIES</div>
              <div className="flow-desc">Actionable match rankings, eligibility checks, and a 90-day strategy.</div>
            </div>
          </div>
        </div>
      </section>

      {/* Intelligence Pillars */}
      <section className="pillars-section">
        <div className="section-header-centered">
          <div className="badge-sub">Why Federal Intelligence Matters</div>
          <h2 className="section-title">The federal government is the world’s largest early-stage backer</h2>
          <p className="section-desc">
            Over $4.3B in non-dilutive funding is deployed to startups annually, yet most founders never apply because solicitations are buried across fragmented agency portals.
          </p>
        </div>

        <div className="pillars-grid">
          <div className="pillar-card">
            <div className="pillar-icon-box">
              <IconDollarSign size={24} />
            </div>
            <h3 className="pillar-title">Zero Equity Dilution</h3>
            <p className="pillar-text">
              Federal SBIR/STTR grants and milestone contracts allow you to fund hard R&D, clinical trials, and pilot deployments without giving up equity or board control.
            </p>
            <div className="pillar-meta">Grants range from $250K to $3.0M+ per company</div>
          </div>

          <div className="pillar-card">
            <div className="pillar-icon-box">
              <IconLandmark size={24} />
            </div>
            <h3 className="pillar-title">Federal Customer Traction</h3>
            <p className="pillar-text">
              Agencies like the VA, DoD, and HHS don’t just grant capital—they are direct buyers. Early pilot contracts pave the pathway to enterprise government procurements.
            </p>
            <div className="pillar-meta">Direct pathway to Phase III Sole-Source contracts</div>
          </div>

          <div className="pillar-card">
            <div className="pillar-icon-box">
              <IconTrendingUp size={24} />
            </div>
            <h3 className="pillar-title">Predictive Match Intelligence</h3>
            <p className="pillar-text">
              We cross-examine your exact technical domain, revenue baseline, and pilot traction against past recipient datasets to score realistic odds before you write a single word.
            </p>
            <div className="pillar-meta">Filtered by historical award records & active solicitations</div>
          </div>
        </div>
      </section>

      {/* Live Sample Teaser */}
      <section className="sample-teaser-section">
        <div className="teaser-banner">
          <div className="teaser-content">
            <div className="teaser-pill">Hackathon Featured Case Study</div>
            <h3 className="teaser-title">Utah-based AI Healthcare Startup</h3>
            <p className="teaser-text">
              See how CareFlow AI (15-person nursing documentation platform) uncovered <strong>7 federal opportunities</strong> worth <strong>$3.2M+ in qualified funding</strong> across NSF, NIH, and ARPA-H.
            </p>
          </div>
          <button type="button" className="btn-primary" onClick={onLoadExample}>
            <span>View Opportunity Map</span>
            <IconArrowRight size={16} />
          </button>
        </div>
      </section>
    </div>
  );
};
