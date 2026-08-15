import React from 'react';
import type { ViewStage } from '../types/opportunity';
import { IconShieldCheck, IconLandmark, IconRefresh, IconCompass } from './icons';

interface NavbarProps {
  currentStage: ViewStage;
  onNavigate: (stage: ViewStage) => void;
  onReset: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentStage, onNavigate, onReset }) => {
  const steps: { stage: ViewStage; label: string; number: string }[] = [
    { stage: 'landing', label: 'Overview', number: '1' },
    { stage: 'intake', label: 'Startup Intake', number: '2' },
    { stage: 'confirm', label: 'Profile Analysis', number: '3' },
    { stage: 'map', label: 'Opportunity Map', number: '4' },
  ];

  const getStepStatus = (stepStage: ViewStage) => {
    const order: ViewStage[] = ['landing', 'intake', 'analyzing', 'confirm', 'map'];
    const currentIndex = order.indexOf(currentStage);
    const stepIndex = order.indexOf(stepStage);

    if (currentStage === stepStage || (currentStage === 'analyzing' && stepStage === 'confirm')) {
      return 'active';
    }
    if (currentIndex > stepIndex) {
      return 'completed';
    }
    return 'upcoming';
  };

  return (
    <header className="site-header">
      <div className="header-inner">
        {/* Brand */}
        <div className="brand-group" onClick={() => onNavigate('landing')} role="button" tabIndex={0}>
          <div className="brand-icon-box">
            <IconCompass size={22} className="brand-icon" />
          </div>
          <div className="brand-text">
            <div className="brand-title">Government Opportunity Map</div>
            <div className="brand-subtitle">Federal Startup Intelligence</div>
          </div>
        </div>

        {/* Progression Stepper */}
        <nav className="nav-stepper" aria-label="Progress">
          {steps.map((step, idx) => {
            const status = getStepStatus(step.stage);
            return (
              <React.Fragment key={step.stage}>
                <button
                  type="button"
                  className={`nav-step-item ${status}`}
                  onClick={() => {
                    if (status === 'completed' || status === 'active') {
                      onNavigate(step.stage);
                    }
                  }}
                  disabled={status === 'upcoming'}
                >
                  <span className="step-num">{step.number}</span>
                  <span className="step-label">{step.label}</span>
                </button>
                {idx < steps.length - 1 && <span className="step-connector" />}
              </React.Fragment>
            );
          })}
        </nav>

        {/* Trust Badge & Actions */}
        <div className="header-actions">
          <div className="federal-trust-pill">
            <IconLandmark size={14} className="trust-icon" />
            <IconShieldCheck size={14} className="trust-badge" />
            <span>Public Federal Data</span>
          </div>

          {currentStage !== 'landing' && (
            <button
              type="button"
              className="btn-text-ghost"
              onClick={onReset}
              title="Reset profile and start new search"
            >
              <IconRefresh size={14} />
              <span>New Search</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
