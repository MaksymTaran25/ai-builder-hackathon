import React, { useState } from 'react';
import type { StartupProfile } from '../types/opportunity';
import { initialMockStartup } from '../data/mockStartup';
import {
  IconSparkles,
  IconArrowRight,
  IconBuilding,
  IconChevronDown,
  IconChevronUp,
  IconDollarSign,
  IconMapPin,
  IconUsers,
  IconBriefcase,
  IconLayers,
  IconTarget,
} from './icons';

interface IntakeProps {
  profile: StartupProfile;
  onChangeProfile: (updated: StartupProfile) => void;
  onSubmit: () => void;
  onLoadExample: () => void;
}

export const Intake: React.FC<IntakeProps> = ({
  profile,
  onChangeProfile,
  onSubmit,
  onLoadExample,
}) => {
  const [showStructured, setShowStructured] = useState(false);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    onChangeProfile({
      ...profile,
      story: text,
    });
  };

  const handleFieldChange = (field: keyof StartupProfile, val: string | number) => {
    onChangeProfile({
      ...profile,
      [field]: val,
    });
  };

  const handleSubmitForm = (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile.story.trim()) {
      onChangeProfile(initialMockStartup);
    }
    onSubmit();
  };

  return (
    <div className="intake-container">
      <div className="intake-header-block">
        <div className="intake-step-badge">Step 2: Startup Intake</div>
        <h1 className="intake-main-title">Tell us about your company.</h1>
        <p className="intake-subtitle">
          Start with your story. We’ll figure out which details matter.
        </p>
      </div>

      <form onSubmit={handleSubmitForm} className="intake-form">
        {/* Dominant Natural Language Textarea */}
        <div className="nl-input-card">
          <div className="nl-header">
            <label htmlFor="startup-story" className="nl-label">
              <IconSparkles size={18} className="nl-icon" />
              <span>Company Narrative & Objectives</span>
            </label>
            <button
              type="button"
              className="btn-sample-fill"
              onClick={onLoadExample}
              title="Fill with the 2026 AI Builder Hackathon sample startup"
            >
              <IconBuilding size={14} />
              <span>Load Hackathon Demo Startup</span>
            </button>
          </div>

          <textarea
            id="startup-story"
            className="nl-textarea"
            rows={5}
            value={profile.story}
            onChange={handleTextChange}
            placeholder="We're a 15-person Utah-based AI healthcare startup building software that reduces administrative work for nurses. We have $1M ARR, have raised $2.5M, and are looking for $500K–$2M to fund product development and hospital pilots."
            required
          />

          <div className="nl-footer-hints">
            <span className="hint-pill">💡 Tip: Include your tech domain, customer type, location, and funding target</span>
            <span className="char-count">{profile.story.length} characters</span>
          </div>
        </div>

        {/* Expandable Structured Details */}
        <div className="structured-accordion-wrap">
          <button
            type="button"
            className="accordion-toggle-btn"
            onClick={() => setShowStructured(!showStructured)}
            aria-expanded={showStructured}
          >
            <div className="accordion-toggle-left">
              <IconLayers size={18} />
              <span>Optional Structured Company Parameters</span>
              <span className="tag-pill-optional">Refine Accuracy</span>
            </div>
            <div className="accordion-toggle-right">
              <span className="accordion-state-label">
                {showStructured ? 'Hide details' : 'Edit details'}
              </span>
              {showStructured ? <IconChevronUp size={18} /> : <IconChevronDown size={18} />}
            </div>
          </button>

          {showStructured && (
            <div className="structured-fields-grid">
              <div className="input-group">
                <label className="input-label">
                  <IconBuilding size={14} /> Company Name
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.name}
                  onChange={(e) => handleFieldChange('name', e.target.value)}
                  placeholder="e.g. CareFlow AI"
                />
              </div>

              <div className="input-group">
                <label className="input-label">
                  <IconBriefcase size={14} /> Industry
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.industry}
                  onChange={(e) => handleFieldChange('industry', e.target.value)}
                  placeholder="e.g. Healthcare Technology"
                />
              </div>

              <div className="input-group">
                <label className="input-label">
                  <IconMapPin size={14} /> Location / State
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.location}
                  onChange={(e) => handleFieldChange('location', e.target.value)}
                  placeholder="e.g. Utah"
                />
              </div>

              <div className="input-group">
                <label className="input-label">
                  <IconUsers size={14} /> Employees (FTE)
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.employees}
                  onChange={(e) => handleFieldChange('employees', e.target.value)}
                  placeholder="e.g. 15"
                />
              </div>

              <div className="input-group">
                <label className="input-label">
                  <IconDollarSign size={14} /> Current Revenue / ARR
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.revenue}
                  onChange={(e) => handleFieldChange('revenue', e.target.value)}
                  placeholder="e.g. $1M ARR"
                />
              </div>

              <div className="input-group">
                <label className="input-label">
                  <IconDollarSign size={14} /> Capital Raised
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.capitalRaised}
                  onChange={(e) => handleFieldChange('capitalRaised', e.target.value)}
                  placeholder="e.g. $2.5M"
                />
              </div>

              <div className="input-group">
                <label className="input-label">
                  <IconDollarSign size={14} /> Capital Required
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.capitalRequired}
                  onChange={(e) => handleFieldChange('capitalRequired', e.target.value)}
                  placeholder="e.g. $500K–$2M"
                />
              </div>

              <div className="input-group">
                <label className="input-label">
                  <IconTarget size={14} /> Target Customers
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.targetCustomers}
                  onChange={(e) => handleFieldChange('targetCustomers', e.target.value)}
                  placeholder="e.g. Hospitals & Health Systems"
                />
              </div>

              <div className="input-group span-2">
                <label className="input-label">
                  <IconLayers size={14} /> Core Technology
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.technology}
                  onChange={(e) => handleFieldChange('technology', e.target.value)}
                  placeholder="e.g. Artificial Intelligence / SaaS"
                />
              </div>

              <div className="input-group span-2">
                <label className="input-label">
                  <IconBriefcase size={14} /> R&D Activities
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.rdActivities}
                  onChange={(e) => handleFieldChange('rdActivities', e.target.value)}
                  placeholder="e.g. Active product development / hospital pilot trials"
                />
              </div>

              <div className="input-group span-2">
                <label className="input-label">
                  <IconTarget size={14} /> Intended Use of Funds
                </label>
                <input
                  type="text"
                  className="text-input"
                  value={profile.useOfFunds}
                  onChange={(e) => handleFieldChange('useOfFunds', e.target.value)}
                  placeholder="e.g. Fund product development and hospital pilots"
                />
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="intake-actions-bar">
          <button type="submit" className="btn-primary-lg" id="analyze-company-btn">
            <span>Analyze my company</span>
            <IconArrowRight size={20} />
          </button>
        </div>
      </form>
    </div>
  );
};
