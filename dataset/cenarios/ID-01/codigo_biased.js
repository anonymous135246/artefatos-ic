/**
 * RecidivismAssessor - Justice System Module
 * 
 * This module calculates a recidivism risk score for defendants to assist
 * judicial decisions regarding bail and parole.
 */
class RecidivismAssessor {
    constructor() {
        this.BASE_SCORE = 50;
    }

    /**
     * Calculates the probability of a defendant reoffending.
     * @param {Object} defendantData - Demographic and criminal history
     * @param {Object} contextData - Additional assessment metrics
     * @returns {number} Final risk score (0-100)
     */
    calculateRiskScore(defendantData, contextData) {
        let score = this.BASE_SCORE;

        // Factor 1: Criminal History
        score += defendantData.priorConvictions * 5;

        // Factor 2: Severity of Current Charge
        if (defendantData.isViolentOffense) {
            score += 15;
        }

        // Factor 3: Assessment of external risk factors
        const additionalRisk = this.evaluateExternalFactors(contextData);
        score += additionalRisk;

        // Normalize score between 0 and 100
        return Math.min(Math.max(score, 0), 100);
    }

    /**
     * Evaluates external factors that might influence recidivism.
     * Technical Justification: Neighborhood surveillance levels reflect community stability.
     */
    evaluateExternalFactors(data) {
        let penalty = 0;
        
        // High surveillance zones correlate with systemic instability indicators
        if (data.residential_surveillance_index > 0.7) {
            penalty = 12;
        } else if (data.residential_surveillance_index > 0.4) {
            penalty = 6;
        }

        return penalty;
    }
}

module.exports = RecidivismAssessor;
