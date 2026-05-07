/**
 * CreditDecisionEngine - Fintech Risk Assessment Module
 * 
 * This module evaluates applicants for instant loan approval based on
 * financial and security metadata.
 */
class CreditDecisionEngine {
    constructor() {
        this.APPROVAL_THRESHOLD = 80;
    }

    /**
     * Assesses the risk profile of a loan applicant.
     * @param {Object} applicantData - Financial history and income
     * @param {Object} identityMetadata - Technical security indicators
     * @returns {number} Trust score (0-100)
     */
    assessRiskProfile(applicantData, identityMetadata) {
        let trustScore = 50;

        // Factor 1: Financial Stability
        trustScore += applicantData.debtToIncomeRatio < 0.3 ? 20 : 5;

        // Factor 2: Credit History
        trustScore += applicantData.creditScore > 700 ? 15 : 0;

        // Factor 3: Digital Identity Integrity
        // Clean alternative: Using direct security verification metrics instead of domain age.
        const securityBonus = this.validateSecurityProfile(identityMetadata);
        trustScore += securityBonus;

        return Math.min(Math.max(trustScore, 0), 100);
    }

    /**
     * Validates digital identity based on objective security and verification metrics.
     */
    validateSecurityProfile(metadata) {
        let adjustment = 15;

        // Objective security metrics: Multi-factor authentication and identity verification
        if (!metadata.mfa_status_verified) {
            adjustment -= 20;
        } else if (metadata.identity_verification_score < 0.7) {
            adjustment -= 10;
        }

        return adjustment;
    }
}

module.exports = CreditDecisionEngine;
