import React, { useState } from 'react';
import type { Opportunity, FitLevel } from '../types/opportunity';
import {
  IconClose,
  IconDollarSign,
  IconCalendar,
  IconClock,
  IconAlertTriangle,
  IconCheckCircle2,
  IconAward,
  IconArrowRight,
  IconCheck,
  IconFileText,
  IconLandmark,
  IconExternalLink,
} from './icons';

interface OpportunityDetailProps {
  opportunity: Opportunity;
  onClose: () => void;
}

export const OpportunityDetail: React.FC<OpportunityDetailProps> = ({ opportunity, onClose }) => {
  const [activeTab, setActiveTab] = useState<'dossier' | 'awards' | 'actionPlan'>('dossier');

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

  return (
    <div className="detail-modal-backdrop" onClick={onClose}>
      <div
        className="detail-modal-content"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        {/* Modal Top Navigation */}
        <div className="modal-header">
          <div className="modal-header-left">
            <div className="modal-agency-pill">
              <IconLandmark size={14} />
              <span>{opportunity.agency}</span>
            </div>
            <span className="modal-program-code">{opportunity.programCode}</span>
          </div>

          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close detail modal"
          >
            <IconClose size={20} />
          </button>
        </div>

        {/* Hero Title & Fit Meta */}
        <div className="modal-hero">
          <div className="modal-hero-top">
            <h2 id="modal-title" className="modal-title">{opportunity.title}</h2>
            <div className="modal-fit-pill-box">
              {getFitBadge(opportunity.fitLevel, opportunity.fitLabel)}
            </div>
          </div>

          <div className="modal-metrics-strip">
            <div className="modal-metric-card">
              <div className="metric-icon-bubble">
                <span className="modal-score-number">{opportunity.matchScore}%</span>
              </div>
              <div className="metric-text-group">
                <span className="metric-sub">Match Confidence</span>
                <span className="metric-highlight">High Technical Fit</span>
              </div>
            </div>

            <div className="modal-metric-card">
              <div className="metric-icon-bubble">
                <IconDollarSign size={20} />
              </div>
              <div className="metric-text-group">
                <span className="metric-sub">Potential Funding</span>
                <span className="metric-highlight">{opportunity.potentialValue}</span>
              </div>
            </div>

            <div className="modal-metric-card">
              <div className="metric-icon-bubble">
                <IconCalendar size={20} />
              </div>
              <div className="metric-text-group">
                <span className="metric-sub">Submission Deadline</span>
                <span className="metric-highlight">{opportunity.deadline}</span>
              </div>
            </div>

            <div className="modal-metric-card">
              <div className="metric-icon-bubble">
                <IconClock size={20} />
              </div>
              <div className="metric-text-group">
                <span className="metric-sub">Time Remaining</span>
                <span className="metric-highlight">{opportunity.daysLeft} Days</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="modal-tab-nav">
          <button
            type="button"
            className={`tab-btn ${activeTab === 'dossier' ? 'active' : ''}`}
            onClick={() => setActiveTab('dossier')}
          >
            <IconFileText size={16} />
            <span>Strategic Advisor Dossier</span>
          </button>

          <button
            type="button"
            className={`tab-btn ${activeTab === 'actionPlan' ? 'active' : ''}`}
            onClick={() => setActiveTab('actionPlan')}
          >
            <IconCheckCircle2 size={16} />
            <span>Action Sequence & Next Steps</span>
          </button>

          <button
            type="button"
            className={`tab-btn ${activeTab === 'awards' ? 'active' : ''}`}
            onClick={() => setActiveTab('awards')}
          >
            <IconAward size={16} />
            <span>Historical Awardees ({opportunity.historicalAwards.length})</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-scrollable-body">
          {activeTab === 'dossier' && (
            <div className="dossier-tab-view">
              {/* Question 1: Why should I care? */}
              <section className="dossier-section care-section">
                <div className="dossier-sec-header">
                  <div className="sec-bubble bubble-care">?</div>
                  <h3 className="sec-heading">Why should I care?</h3>
                </div>
                <div className="sec-content-box">
                  <p className="primary-care-text">{opportunity.detailedOverview.whyShouldICare}</p>
                  <div className="fit-signals-tag-list">
                    <span className="tag-label">Matched Startup Signals:</span>
                    {opportunity.whyFit.map((fit, idx) => (
                      <span key={idx} className="fit-signal-tag">
                        <IconCheck size={13} /> {fit}
                      </span>
                    ))}
                  </div>
                </div>
              </section>

              {/* Question 2: What could make me ineligible? */}
              <section className="dossier-section ineligibility-section">
                <div className="dossier-sec-header">
                  <div className="sec-bubble bubble-warn">
                    <IconAlertTriangle size={16} />
                  </div>
                  <h3 className="sec-heading">What could make me ineligible?</h3>
                </div>
                <div className="sec-content-box warning-box">
                  <ul className="dossier-bullet-list">
                    {opportunity.detailedOverview.whatCouldMakeMeIneligible.map((item, idx) => (
                      <li key={idx} className="dossier-bullet-item warning">
                        <span className="item-marker">⚠️</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </section>

              {/* Question 3: What should I verify? */}
              <section className="dossier-section verify-section">
                <div className="dossier-sec-header">
                  <div className="sec-bubble bubble-verify">
                    <IconCheckCircle2 size={16} />
                  </div>
                  <h3 className="sec-heading">What should I verify?</h3>
                </div>
                <div className="sec-content-box info-box">
                  <ul className="dossier-bullet-list">
                    {opportunity.detailedOverview.whatShouldIVerify.map((item, idx) => (
                      <li key={idx} className="dossier-bullet-item info">
                        <span className="item-marker">🔍</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </section>

              {/* Question 4: What should I do next? */}
              <section className="dossier-section next-section">
                <div className="dossier-sec-header">
                  <div className="sec-bubble bubble-next">
                    <IconArrowRight size={16} />
                  </div>
                  <h3 className="sec-heading">What should I do next?</h3>
                </div>
                <div className="sec-content-box next-box">
                  <ul className="dossier-bullet-list">
                    {opportunity.detailedOverview.whatShouldIDoNext.map((item, idx) => (
                      <li key={idx} className="dossier-bullet-item action">
                        <span className="item-marker">➔</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </section>
            </div>
          )}

          {activeTab === 'actionPlan' && (
            <div className="action-plan-tab-view">
              <div className="action-plan-intro">
                <h3>Recommended Founder Action Sequence</h3>
                <p>Follow this milestone pathway to submit a competitive application without disrupting product roadmap execution.</p>
              </div>

              <div className="action-timeline-list">
                {opportunity.detailedOverview.actionSequence.map((step) => (
                  <div key={step.step} className="action-timeline-card">
                    <div className="step-number-circle">{step.step}</div>
                    <div className="step-body">
                      <div className="step-header">
                        <h4 className="step-title">{step.title}</h4>
                        <span className="step-timeline-pill">{step.timeline}</span>
                      </div>
                      <p className="step-detail">{step.detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'awards' && (
            <div className="awards-tab-view">
              <div className="awards-intro-banner">
                <div className="intel-summary-head">
                  <IconAward size={20} className="intel-icon" />
                  <h4>Historical Award Intelligence: Who else received this money?</h4>
                </div>
                <p>
                  Analyzing recent recipient profiles in clinical AI and workflow software helps benchmark grant competitiveness and typical award sizing.
                </p>
                <div className="summary-pills-row">
                  <span className="summary-pill">
                    <strong>{opportunity.historicalIntelligence.similarCompaniesFunded}</strong> Similar Startups Funded
                  </span>
                  <span className="summary-pill">
                    <strong>{opportunity.historicalIntelligence.totalHistoricalAwards}</strong> Total Capital Deployed
                  </span>
                  <span className="summary-pill">
                    <strong>{opportunity.historicalIntelligence.medianAward}</strong> Median Award Sizing
                  </span>
                  <span className="summary-pill">
                    <strong>{opportunity.historicalIntelligence.localRecipients}</strong>
                  </span>
                </div>
              </div>

              {/* Historical Award Table */}
              <div className="table-responsive">
                <table className="historical-table">
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Program</th>
                      <th>Agency</th>
                      <th>Amount</th>
                      <th>Year</th>
                      <th>Location</th>
                      <th>Project Focus</th>
                    </tr>
                  </thead>
                  <tbody>
                    {opportunity.historicalAwards.map((award) => (
                      <tr key={award.id}>
                        <td className="company-cell">
                          <strong>{award.company}</strong>
                        </td>
                        <td>
                          <span className="program-badge">{award.program}</span>
                        </td>
                        <td>{award.agency}</td>
                        <td className="amount-cell">{award.amount}</td>
                        <td>{award.year}</td>
                        <td className="location-cell">{award.location}</td>
                        <td className="project-cell">{award.projectTitle}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <div className="footer-left-info">
            <span className="footer-agency-note">Official solicitation portal link & SAM.gov validation ready</span>
          </div>

          <div className="footer-action-buttons">
            <button type="button" className="btn-secondary" onClick={onClose}>
              <span>Close Dossier</span>
            </button>

            <button
              type="button"
              className="btn-primary"
              onClick={() => {
                alert(`Exporting 90-day action checklist for ${opportunity.title}`);
              }}
            >
              <span>Export Action Checklist</span>
              <IconExternalLink size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
