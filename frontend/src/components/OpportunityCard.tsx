import React from 'react';
import type { Opportunity, FitLevel } from '../types/opportunity';
import {
  IconCheck,
  IconAlertTriangle,
  IconArrowRight,
  IconCalendar,
  IconDollarSign,
  IconAward,
  IconMapPin,
  IconClock,
} from './icons';

interface OpportunityCardProps {
  opportunity: Opportunity;
  onExplore: (opp: Opportunity) => void;
}

export const OpportunityCard: React.FC<OpportunityCardProps> = ({ opportunity, onExplore }) => {
  const getFitBadge = (level: FitLevel, label: string) => {
    switch (level) {
      case 'likely':
        return (
          <span className="fit-pill fit-likely">
            <span className="fit-dot dot-likely" />
            <span>{label}</span>
          </span>
        );
      case 'potential':
        return (
          <span className="fit-pill fit-potential">
            <span className="fit-dot dot-potential" />
            <span>{label}</span>
          </span>
        );
      case 'adjacent':
        return (
          <span className="fit-pill fit-adjacent">
            <span className="fit-dot dot-adjacent" />
            <span>{label}</span>
          </span>
        );
      case 'unlikely':
        return (
          <span className="fit-pill fit-unlikely">
            <span className="fit-dot dot-unlikely" />
            <span>{label}</span>
          </span>
        );
    }
  };

  const getScoreColorClass = (score: number) => {
    if (score >= 85) return 'score-high';
    if (score >= 70) return 'score-medium';
    if (score >= 50) return 'score-adjacent';
    return 'score-low';
  };

  return (
    <article className={`opp-card fit-${opportunity.fitLevel}`}>
      {/* Header: Score, Program Title, Agency, Fit Badge */}
      <div className="opp-card-top">
        <div className="opp-header-row">
          <div className={`opp-score-badge ${getScoreColorClass(opportunity.matchScore)}`}>
            <span className="score-num">{opportunity.matchScore}%</span>
            <span className="score-label">Match</span>
          </div>

          <div className="opp-title-area">
            <div className="opp-agency-meta">
              <span className="agency-name">{opportunity.agency}</span>
              <span className="bullet-sep">•</span>
              <span className="program-code">{opportunity.programCode}</span>
            </div>
            <h3 className="opp-title">{opportunity.title}</h3>
          </div>

          <div className="opp-fit-indicator">
            {getFitBadge(opportunity.fitLevel, opportunity.fitLabel)}
          </div>
        </div>

        {/* Quick Value & Timeline Row */}
        <div className="opp-quick-metrics">
          <div className="metric-cell">
            <IconDollarSign size={16} className="metric-icon" />
            <div className="metric-content">
              <span className="metric-label">Potential value:</span>
              <span className="metric-val highlight-val">{opportunity.potentialValue}</span>
            </div>
          </div>

          <div className="metric-cell">
            <IconCalendar size={16} className="metric-icon" />
            <div className="metric-content">
              <span className="metric-label">Deadline:</span>
              <span className="metric-val">{opportunity.deadline}</span>
            </div>
          </div>

          {opportunity.daysLeft <= 90 && (
            <div className="metric-cell closing-tag">
              <IconClock size={15} />
              <span>{opportunity.daysLeft} days left</span>
            </div>
          )}
        </div>
      </div>

      {/* Summary Snippet */}
      <p className="opp-summary">{opportunity.summary}</p>

      {/* Two Column Section: Why we think you're a fit vs Potential concerns */}
      <div className="opp-analysis-dual-grid">
        {/* Why fit */}
        <div className="analysis-box why-fit-box">
          <div className="analysis-box-header">
            <span className="box-icon-wrap icon-check">
              <IconCheck size={14} />
            </span>
            <span className="box-title">Why we think you’re a fit</span>
          </div>
          <ul className="bullet-list fit-bullets">
            {opportunity.whyFit.map((item, idx) => (
              <li key={idx} className="bullet-item">
                <span className="bullet-icon check-mark">✓</span>
                <span className="bullet-text">{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Potential concerns */}
        <div className="analysis-box concerns-box">
          <div className="analysis-box-header">
            <span className="box-icon-wrap icon-warn">
              <IconAlertTriangle size={14} />
            </span>
            <span className="box-title">Potential concerns</span>
          </div>
          <ul className="bullet-list concern-bullets">
            {opportunity.concerns.map((item, idx) => (
              <li key={idx} className="bullet-item">
                <span className="bullet-icon warn-mark">⚠</span>
                <span className="bullet-text">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Historical Intelligence Row */}
      <div className="historical-intel-banner">
        <div className="intel-header">
          <IconAward size={16} className="award-icon" />
          <span className="intel-title">Historical intelligence</span>
        </div>

        <div className="intel-metrics-grid">
          <div className="intel-metric">
            <span className="intel-num">{opportunity.historicalIntelligence.similarCompaniesFunded}</span>
            <span className="intel-sub">similar companies funded</span>
          </div>

          <div className="intel-metric">
            <span className="intel-num">{opportunity.historicalIntelligence.totalHistoricalAwards}</span>
            <span className="intel-sub">total historical awards</span>
          </div>

          <div className="intel-metric">
            <span className="intel-num">{opportunity.historicalIntelligence.medianAward}</span>
            <span className="intel-sub">median award</span>
          </div>

          <div className="intel-metric local-tag">
            <span className="intel-num">
              <IconMapPin size={14} /> {opportunity.historicalIntelligence.localRecipients}
            </span>
            <span className="intel-sub">local / state precedents</span>
          </div>
        </div>
      </div>

      {/* Card Action Footer */}
      <div className="opp-card-footer">
        <span className="category-tag">{opportunity.category}</span>
        <button
          type="button"
          className="btn-explore"
          onClick={() => onExplore(opportunity)}
          id={`explore-${opportunity.id}`}
        >
          <span>Explore opportunity</span>
          <IconArrowRight size={16} />
        </button>
      </div>
    </article>
  );
};
