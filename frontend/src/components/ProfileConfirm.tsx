import React, { useEffect, useState } from 'react';
import type { StartupProfile } from '../types/opportunity';
import {
  IconCheckCircle2,
  IconSparkles,
  IconArrowRight,
  IconEdit,
  IconBriefcase,
  IconLayers,
  IconMapPin,
  IconUsers,
  IconDollarSign,
  IconTarget,
} from './icons';

interface ProfileConfirmProps {
  profile: StartupProfile;
  onConfirm: () => void;
  onEdit: () => void;
  isAnalyzing: boolean;
  onFinishAnalysis: () => void;
}

const ANALYSIS_STEPS = [
  'Extracting company signals from natural language narrative...',
  'Mapping technical domain: AI/NLP Healthcare Workflow Automation...',
  'Querying SAM.gov, SBIR.gov & Grants.gov active open solicitations...',
  'Synthesizing historical award matching models across 11 federal agencies...',
  'Complete! Synthesized opportunity matrix ready.',
];

export const ProfileConfirm: React.FC<ProfileConfirmProps> = ({
  profile,
  onConfirm,
  onEdit,
  isAnalyzing,
  onFinishAnalysis,
}) => {
  const [analysisStepIndex, setAnalysisStepIndex] = useState(0);

  useEffect(() => {
    if (!isAnalyzing) return;

    const interval = setInterval(() => {
      setAnalysisStepIndex((prev) => {
        if (prev < ANALYSIS_STEPS.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          setTimeout(() => {
            onFinishAnalysis();
          }, 400);
          return prev;
        }
      });
    }, 450);

    return () => clearInterval(interval);
  }, [isAnalyzing, onFinishAnalysis]);

  if (isAnalyzing) {
    return (
      <div className="analysis-loading-container">
        <div className="analysis-card">
          <div className="pulsing-radar-box">
            <IconSparkles size={36} className="radar-icon-spin" />
          </div>

          <h2 className="analysis-title">Analyzing Company Profile</h2>
          <p className="analysis-subtitle">
            Cross-referencing your company parameters against $4.3B in federal solicitations...
          </p>

          <div className="analysis-progress-bar-wrap">
            <div
              className="analysis-progress-bar-fill"
              style={{
                width: `${((analysisStepIndex + 1) / ANALYSIS_STEPS.length) * 100}%`,
              }}
            />
          </div>

          <div className="analysis-step-text">
            <span className="step-live-dot" />
            <span>{ANALYSIS_STEPS[analysisStepIndex]}</span>
          </div>
        </div>
      </div>
    );
  }

  const profileAttributes = [
    {
      label: 'Industry',
      value: profile.industry || 'Healthcare Technology',
      icon: <IconBriefcase size={16} />,
      highlight: true,
    },
    {
      label: 'Technology',
      value: profile.technology || 'Artificial Intelligence / SaaS',
      icon: <IconLayers size={16} />,
      highlight: true,
    },
    {
      label: 'Location',
      value: profile.location || 'Utah',
      icon: <IconMapPin size={16} />,
    },
    {
      label: 'Employees',
      value: profile.employees ? `${profile.employees} FTE` : '15 FTE',
      icon: <IconUsers size={16} />,
    },
    {
      label: 'Revenue',
      value: profile.revenue || '$1M ARR',
      icon: <IconDollarSign size={16} />,
      highlight: true,
    },
    {
      label: 'Capital Raised',
      value: profile.capitalRaised || '$2.5M',
      icon: <IconDollarSign size={16} />,
    },
    {
      label: 'Funding Need',
      value: profile.fundingNeed || '$500K–$2M',
      icon: <IconDollarSign size={16} />,
      highlight: true,
    },
    {
      label: 'R&D Activities',
      value: profile.rdActivities || 'Active product development',
      icon: <IconBriefcase size={16} />,
    },
    {
      label: 'Target Customers',
      value: profile.targetCustomers || 'Hospitals',
      icon: <IconTarget size={16} />,
    },
  ];

  return (
    <div className="confirm-container">
      <div className="confirm-header-block">
        <div className="confirm-step-badge">Step 3: Verification</div>
        <h1 className="confirm-main-title">Here’s what we understood</h1>
        <p className="confirm-subtitle">
          We extracted key signals to match you with agency priorities and eligibility criteria.
        </p>
      </div>

      {/* Narrative Snippet */}
      <div className="narrative-summary-card">
        <div className="narrative-label">
          <IconSparkles size={16} />
          <span>Analyzed Startup Narrative</span>
        </div>
        <p className="narrative-quote">“{profile.story}”</p>
      </div>

      {/* Extracted Structured Profile Cards Grid */}
      <div className="extracted-grid">
        {profileAttributes.map((attr, idx) => (
          <div key={idx} className={`extracted-card ${attr.highlight ? 'highlight-border' : ''}`}>
            <div className="extracted-card-header">
              <span className="attr-icon">{attr.icon}</span>
              <span className="attr-label">{attr.label}</span>
            </div>
            <div className="attr-value">{attr.value}</div>
          </div>
        ))}
      </div>

      {/* Confirmation Callout & Actions */}
      <div className="confirm-action-box">
        <div className="confirm-prompt-text">
          <IconCheckCircle2 size={20} className="check-accent" />
          <span>Does this look right?</span>
        </div>

        <div className="confirm-button-row">
          <button
            type="button"
            className="btn-secondary"
            onClick={onEdit}
            id="edit-profile-btn"
          >
            <IconEdit size={16} />
            <span>Edit profile</span>
          </button>

          <button
            type="button"
            className="btn-primary-lg"
            onClick={onConfirm}
            id="find-opps-btn"
          >
            <span>Looks good — find opportunities</span>
            <IconArrowRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};
