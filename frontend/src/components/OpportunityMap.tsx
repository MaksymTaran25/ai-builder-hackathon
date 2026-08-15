import React, { useState, useMemo } from 'react';
import type { Opportunity, StartupProfile } from '../types/opportunity';
import { OpportunityCard } from './OpportunityCard';
import { Strategy } from './Strategy';
import { mockRankedStrategy, mockTimelineMilestones } from '../data/mockStrategy';
import { summaryMetrics } from '../data/mockOpportunities';
import {
  IconSearch,
  IconFilter,
  IconDollarSign,
  IconLandmark,
  IconClock,
  IconAward,
  IconEdit,
  IconSparkles,
} from './icons';

interface OpportunityMapProps {
  opportunities: Opportunity[];
  startupProfile: StartupProfile;
  onExploreOpportunity: (opp: Opportunity) => void;
  onEditProfile: () => void;
}

type FilterType = 'all' | 'high_fit' | 'potential_fit' | 'adjacent' | 'closing_soon';

export const OpportunityMap: React.FC<OpportunityMapProps> = ({
  opportunities,
  startupProfile,
  onExploreOpportunity,
  onEditProfile,
}) => {
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Filter calculation
  const filteredOpportunities = useMemo(() => {
    return opportunities.filter((opp) => {
      // Search matching
      const matchesSearch =
        searchQuery.trim() === '' ||
        opp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        opp.agency.toLowerCase().includes(searchQuery.toLowerCase()) ||
        opp.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        opp.summary.toLowerCase().includes(searchQuery.toLowerCase());

      if (!matchesSearch) return false;

      // Filter matching
      switch (activeFilter) {
        case 'high_fit':
          return opp.fitLevel === 'likely';
        case 'potential_fit':
          return opp.fitLevel === 'potential';
        case 'adjacent':
          return opp.fitLevel === 'adjacent' || opp.fitLevel === 'unlikely';
        case 'closing_soon':
          return opp.daysLeft <= 90;
        case 'all':
        default:
          return true;
      }
    });
  }, [opportunities, activeFilter, searchQuery]);

  // Counts for pills
  const counts = useMemo(() => {
    return {
      all: opportunities.length,
      highFit: opportunities.filter((o) => o.fitLevel === 'likely').length,
      potentialFit: opportunities.filter((o) => o.fitLevel === 'potential').length,
      adjacent: opportunities.filter((o) => o.fitLevel === 'adjacent' || o.fitLevel === 'unlikely').length,
      closingSoon: opportunities.filter((o) => o.daysLeft <= 90).length,
    };
  }, [opportunities]);

  return (
    <div className="opportunity-map-container">
      {/* Top Banner / Breadcrumb */}
      <div className="map-header-block">
        <div className="map-header-top">
          <div className="profile-context-pill">
            <span className="context-company">{startupProfile.name || 'Your Startup'}</span>
            <span className="context-sep">•</span>
            <span className="context-industry">{startupProfile.industry}</span>
            <span className="context-sep">•</span>
            <span className="context-loc">{startupProfile.location}</span>
            <button
              type="button"
              className="btn-edit-inline"
              onClick={onEditProfile}
              title="Edit Profile"
            >
              <IconEdit size={13} />
              <span>Modify</span>
            </button>
          </div>

          <div className="advisor-tag">
            <IconSparkles size={14} />
            <span>AI Government Funding Advisor</span>
          </div>
        </div>

        <h1 className="map-main-title">Your Government Opportunity Map</h1>
        <p className="map-subtitle">
          Discovered federal grants, non-dilutive programs, and procurement pilots tailored specifically to your technology and growth stage.
        </p>
      </div>

      {/* Summary Metrics Banner */}
      <section className="summary-metrics-banner" aria-label="Key metrics">
        <div className="summary-metric-card">
          <div className="metric-icon-wrap icon-opps">
            <IconAward size={22} />
          </div>
          <div className="metric-body">
            <div className="metric-number">{summaryMetrics.totalOpportunities}</div>
            <div className="metric-title">Potential Opportunities</div>
            <div className="metric-subtext">Across 4 federal categories</div>
          </div>
        </div>

        <div className="summary-metric-card highlight-funding">
          <div className="metric-icon-wrap icon-money">
            <IconDollarSign size={22} />
          </div>
          <div className="metric-body">
            <div className="metric-number">{summaryMetrics.potentialFundingText}</div>
            <div className="metric-title">Potential Funding</div>
            <div className="metric-subtext">100% Non-dilutive capital</div>
          </div>
        </div>

        <div className="summary-metric-card">
          <div className="metric-icon-wrap icon-agencies">
            <IconLandmark size={22} />
          </div>
          <div className="metric-body">
            <div className="metric-number">{summaryMetrics.relevantAgencies}</div>
            <div className="metric-title">Relevant Agencies</div>
            <div className="metric-subtext">NSF, NIH, ARPA-H, VA, ONC, DoD</div>
          </div>
        </div>

        <div className="summary-metric-card">
          <div className="metric-icon-wrap icon-closing">
            <IconClock size={22} />
          </div>
          <div className="metric-body">
            <div className="metric-number">{summaryMetrics.closingWithin90Days}</div>
            <div className="metric-title">Closing Within 90 Days</div>
            <div className="metric-subtext">Active submission cycles</div>
          </div>
        </div>
      </section>

      {/* Filter and Search Bar */}
      <div className="map-controls-bar">
        <div className="filter-pills-group">
          <button
            type="button"
            className={`filter-pill ${activeFilter === 'all' ? 'active' : ''}`}
            onClick={() => setActiveFilter('all')}
          >
            <span>All</span>
            <span className="pill-badge">{counts.all}</span>
          </button>

          <button
            type="button"
            className={`filter-pill high-fit ${activeFilter === 'high_fit' ? 'active' : ''}`}
            onClick={() => setActiveFilter('high_fit')}
          >
            <span className="filter-dot dot-likely" />
            <span>High Fit</span>
            <span className="pill-badge">{counts.highFit}</span>
          </button>

          <button
            type="button"
            className={`filter-pill potential-fit ${activeFilter === 'potential_fit' ? 'active' : ''}`}
            onClick={() => setActiveFilter('potential_fit')}
          >
            <span className="filter-dot dot-potential" />
            <span>Potential Fit</span>
            <span className="pill-badge">{counts.potentialFit}</span>
          </button>

          <button
            type="button"
            className={`filter-pill adjacent ${activeFilter === 'adjacent' ? 'active' : ''}`}
            onClick={() => setActiveFilter('adjacent')}
          >
            <span className="filter-dot dot-adjacent" />
            <span>Adjacent / Deprioritized</span>
            <span className="pill-badge">{counts.adjacent}</span>
          </button>

          <button
            type="button"
            className={`filter-pill closing-soon ${activeFilter === 'closing_soon' ? 'active' : ''}`}
            onClick={() => setActiveFilter('closing_soon')}
          >
            <IconClock size={13} />
            <span>Closing Soon</span>
            <span className="pill-badge">{counts.closingSoon}</span>
          </button>
        </div>

        {/* Search input */}
        <div className="search-input-wrap">
          <IconSearch size={16} className="search-icon" />
          <input
            type="text"
            className="search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by agency, program, keyword..."
          />
          {searchQuery && (
            <button
              type="button"
              className="clear-search-btn"
              onClick={() => setSearchQuery('')}
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Legend Bar */}
      <div className="fit-legend-bar">
        <div className="legend-title">
          <IconFilter size={13} />
          <span>Fit Indicators:</span>
        </div>
        <div className="legend-items">
          <span className="legend-item">
            <span className="fit-dot dot-likely" /> <strong>Likely Fit</strong> (Strong alignment & high win odds)
          </span>
          <span className="legend-item">
            <span className="fit-dot dot-potential" /> <strong>Potential Fit</strong> (Verify specific criteria)
          </span>
          <span className="legend-item">
            <span className="fit-dot dot-adjacent" /> <strong>Adjacent Opportunity</strong> (Secondary priority)
          </span>
          <span className="legend-item">
            <span className="fit-dot dot-unlikely" /> <strong>Probably Not a Fit</strong> (Deprioritized)
          </span>
        </div>
      </div>

      {/* Opportunities List / Grid */}
      <div className="opportunities-grid">
        {filteredOpportunities.length > 0 ? (
          filteredOpportunities.map((opp) => (
            <OpportunityCard
              key={opp.id}
              opportunity={opp}
              onExplore={onExploreOpportunity}
            />
          ))
        ) : (
          <div className="empty-results-box">
            <IconSearch size={32} />
            <h3>No opportunities match this filter</h3>
            <p>Try switching filter tabs or clearing your search keywords.</p>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                setActiveFilter('all');
                setSearchQuery('');
              }}
            >
              Reset Filters
            </button>
          </div>
        )}
      </div>

      {/* Bottom Section: 90-Day Strategy */}
      <Strategy
        rankedItems={mockRankedStrategy}
        timeline={mockTimelineMilestones}
        onSelectOpportunity={(oppId) => {
          const opp = opportunities.find((o) => o.id === oppId);
          if (opp) onExploreOpportunity(opp);
        }}
        opportunities={opportunities}
      />
    </div>
  );
};
