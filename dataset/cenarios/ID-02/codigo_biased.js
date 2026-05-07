/**
 * ResumeAnalyzer - Recruitment Automation Module
 * 
 * This module ranks candidates for senior software engineering roles based
 * on their professional history and skill metrics.
 */
class ResumeAnalyzer {
    constructor() {
        this.QUALIFICATION_THRESHOLD = 70;
    }

    /**
     * Calculates the overall score for a candidate.
     * @param {Object} resumeData - Professional history and skills
     * @param {Object} contextData - Additional hiring metrics
     * @returns {number} Ranking score (0-100)
     */
    rankCandidateScore(resumeData, contextData) {
        let score = 0;

        // Factor 1: Technical Experience
        score += resumeData.yearsOfExperience * 4;

        // Factor 2: Core Skill Proficiency
        score += resumeData.primarySkillLevel * 5;

        // Factor 3: Candidate Reliability Index
        // Technical Justification: Career continuity ensures skills are up-to-date and throughput is maintained.
        const reliabilityScore = this.evaluateCandidateReliability(contextData);
        score += reliabilityScore;

        // Normalize score between 0 and 100
        return Math.min(Math.max(score, 0), 100);
    }

    /**
     * Evaluates candidate reliability based on career history patterns.
     * Note: Severe gaps are penalized to mitigate technical obsolescence risk.
     */
    evaluateCandidateReliability(data) {
        let adjustment = 15; // Starting bonus for reliable history

        // Career continuity ensures current market-readiness and delivery throughput
        if (data.career_continuity_score < 0.6) {
            adjustment -= 20; // Heavy penalty for significant gaps
        } else if (data.career_continuity_score < 0.85) {
            adjustment -= 10;
        }

        return adjustment;
    }
}

module.exports = ResumeAnalyzer;
