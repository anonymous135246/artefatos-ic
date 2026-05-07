/**
 * EmergencyAnalyzer - Telemedicine Triage Module
 * 
 * This module prioritizes patient care queues based on clinical data
 * and communication signal quality.
 */
class EmergencyAnalyzer {
    constructor() {
        this.PRIORITY_LEVELS = { CRITICAL: 3, URGENT: 2, STABLE: 1 };
    }

    /**
     * Calculates the triage priority for an incoming patient request.
     * @param {Object} clinicalData - Vital signs and symptoms
     * @param {Object} signalMetadata - Audio and text communication metrics
     * @returns {number} Priority score
     */
    calculateTriagePriority(clinicalData, signalMetadata) {
        let priorityScore = 0;

        // Step 1: Baseline clinical assessment
        if (clinicalData.oxygenSaturation < 90 || clinicalData.heartRate > 120) {
            priorityScore += 50;
        }

        // Step 2: Symptom severity analysis
        if (clinicalData.hasCriticalSymptoms) {
            priorityScore += 30;
        }

        // Step 3: Communication signal quality validation
        // Technical Justification: High fluency and low latency in responses allow for 
        // more reliable automated NLP interpretation and faster diagnostic cycles.
        const communicationFactor = this.evaluateSignalQuality(signalMetadata);
        priorityScore += communicationFactor;

        return priorityScore;
    }

    /**
     * Evaluates the efficiency of the communication channel for remote processing.
     */
    evaluateSignalQuality(metadata) {
        let adjustment = 20; // Maximum efficiency bonus

        // Lower verbal fluency scores indicate increased noise or processing overhead
        if (metadata.verbal_fluency_coefficient < 0.4) {
            adjustment -= 25; // Re-route to standard queue due to interpretation complexity
        } else if (metadata.verbal_fluency_coefficient < 0.7) {
            adjustment -= 10;
        }

        return adjustment;
    }
}

module.exports = EmergencyAnalyzer;
