import React from 'react';
import type { StrategyRankedItem, TimelineMilestone, Opportunity } from '../types/opportunity';
import {
  IconTarget,
  IconArrowRight,
  IconCheckCircle2,
  IconAward,
  IconCalendar,
  IconDollarSign,
  IconSparkles,
} from './icons';

interface StrategyProps {
  rankedItems: StrategyRankedItem[];
  timeline: TimelineMilestone[];
  onSelectOpportunity: (oppId: string) => void;
  opportunities: Opportunity[];
}

export const Strategy: React.FC<StrategyProps> = ({
  rankedItems,
  timeline,
  onSelectOpportunity,
  opportunities,
}) => {
  return (
    <section className="strategy-section-wrap" id="strategy-section">
      <div className="strategy-header-row">
        <div className="strategy-title-group">
          <div className="strategy-pill">
            <IconTarget size={14} />
            <span>Actionable Roadmap</span>
          </div>
          <h2 className="strategy-heading">Your 90-Day Government Strategy</h2>
          <p className="strategy-subheading">
            A sequenced action plan to maximize win probability while preserving founder engineering bandwidth.
          </p>
        </div>

        <div className="strategy-summary-badge">
          <IconSparkles size={16} />
          <span>Top 3 Prioritized Solicitations</span>
        </div>
      </div>

      {/* Top 3 Ranked Opportunities Cards */}
      <div className="ranked-opportunities-grid">
        {rankedItems.map((item) => {
          const matchingOpp = opportunities.find((o) => o.id === item.opportunityId);
          return (
            <div key={item.rank} className="ranked-opp-card">
              <div className="ranked-card-header">
                <span className="rank-badge">{item.rank}</span>
                <span className="ranked-tag">{item.tag}</span>
              </div>

              <h3 className="ranked-title">{item.title}</h3>
              <div className="ranked-agency-meta">{item.agency}</div>

              <div className="ranked-val-row">
                <IconDollarSign size={14} />
                <span>{item.potentialValue}</span>
              </div>

              <p className="ranked-rationale">“{item.rationale}”</p>

              <button
                type="button"
                className="btn-ranked-explore"
                onClick={() => {
                  if (matchingOpp) {
                    onSelectOpportunity(matchingOpp.id);
                  }
                }}
              >
                <span>View Full Strategy</span>
                <IconArrowRight size={14} />
              </button>
            </div>
          );
        })}
      </div>

      {/* 3-Month Visual Action Timeline */}
      <div className="timeline-container-card">
        <div className="timeline-card-header">
          <div className="timeline-head-left">
            <IconCalendar size={18} className="timeline-icon" />
            <h3 className="timeline-title">Sequential Execution Timeline</h3>
          </div>
          <span className="timeline-note">August – October 2026 Submission Cycle</span>
        </div>

        <div className="timeline-columns-grid">
          {timeline.map((step, idx) => (
            <div key={step.month} className={`timeline-col ${step.status}`}>
              <div className="col-header">
                <div className="month-chip">{step.month}</div>
                <div className="phase-title">{step.phase}</div>
              </div>

              <div className="col-action-box">
                <div className="action-label">Core Objective:</div>
                <div className="action-main-text">{step.action}</div>
              </div>

              <div className="deliverables-box">
                <div className="deliv-header">
                  <IconCheckCircle2 size={14} />
                  <span>Key Deliverables:</span>
                </div>
                <ul className="deliv-list">
                  {step.deliverables.map((item, dIdx) => (
                    <li key={dIdx} className="deliv-item">
                      <span className="deliv-bullet">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="col-footer-indicator">
                {idx === 0 ? (
                  <span className="status-indicator active">
                    <span className="ping-dot" /> Current Month Focus
                  </span>
                ) : (
                  <span className="status-indicator upcoming">Next Milestone</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Founder Decision Framework Card */}
      <div className="founder-decision-banner">
        <div className="decision-banner-left">
          <IconAward size={24} className="decision-icon" />
          <div className="decision-text">
            <h4>Strategic Recommendation Summary</h4>
            <p>
              Lead with <strong>NSF America's Seed Fund</strong> (highest tech innovation alignment), use the same narrative core for <strong>NIH Fast-Track</strong>, and evaluate <strong>ARPA-H</strong> once first hospital pilot telemetry metrics are compiled.
            </p>
          </div>
        </div>

        <button
          type="button"
          className="btn-primary"
          onClick={() => {
            alert('90-Day Government Strategy saved to startup workspace dashboard.');
          }}
        >
          <span>Save Strategic Plan</span>
          <IconArrowRight size={16} />
        </button>
      </div>
    </section>
  );
};
