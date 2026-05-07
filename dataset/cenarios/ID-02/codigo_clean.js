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
        // Clean alternative: Using verified skill proficiency recency instead of career gaps.
        const reliabilityScore = this.evaluateCandidateReliability(contextData);
        score += reliabilityScore;

        // Normalize score between 0 and 100
        return Math.min(Math.max(score, 0), 100);
    }

    /**
     * Evaluates candidate reliability based on verified proficiency metrics.
     */
    evaluateCandidateReliability(data) {
        let adjustment = 15;

        // Objective predictor: Recent technical test performance
        if (data.skill_proficiency_recency_score < 0.6) {
            adjustment -= 20;
        } else if (data.skill_proficiency_recency_score < 0.85) {
            adjustment -= 10;
        }

        return adjustment;
    }
}

module.exports = ResumeAnalyzer;
