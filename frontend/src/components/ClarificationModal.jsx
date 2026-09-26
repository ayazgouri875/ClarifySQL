import React, { useState } from "react";
import { AlertCircle, HelpCircle, ArrowRight, Sparkles, CheckCircle } from "lucide-react";

export default function ClarificationModal({ ambiguity, onSubmit, onCancel }) {
  const [selectedOption, setSelectedOption] = useState(
    ambiguity?.default_option || (ambiguity?.options && ambiguity.options[0]) || ""
  );

  if (!ambiguity) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(3, 7, 18, 0.8)",
        backdropFilter: "blur(8px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 100,
        padding: "20px"
      }}
    >
      <div
        className="glass-card"
        style={{
          width: "100%",
          maxWidth: "580px",
          background: "linear-gradient(180deg, #161F33 0%, #0E1626 100%)",
          border: "1px solid rgba(99, 102, 241, 0.3)",
          boxShadow: "0 20px 50px -10px rgba(0, 0, 0, 0.8), 0 0 30px rgba(99, 102, 241, 0.2)",
          padding: "28px",
          animation: "scaleIn 0.25s ease-out"
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", gap: "14px", marginBottom: "18px" }}>
          <div
            style={{
              width: "42px",
              height: "42px",
              borderRadius: "12px",
              background: "rgba(245, 158, 11, 0.15)",
              border: "1px solid rgba(245, 158, 11, 0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#F59E0B",
              flexShrink: 0
            }}
          >
            <HelpCircle size={24} />
          </div>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <span className="badge badge-warning" style={{ textTransform: "uppercase" }}>
                {ambiguity.category} Ambiguity Detected
              </span>
              {ambiguity.detected_term && (
                <span
                  style={{
                    fontSize: "12px",
                    color: "#94A3B8",
                    background: "rgba(255, 255, 255, 0.05)",
                    padding: "2px 8px",
                    borderRadius: "6px"
                  }}
                >
                  "{ambiguity.detected_term}"
                </span>
              )}
            </div>
            <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#FFF" }}>Clarification Needed</h2>
          </div>
        </div>

        {/* Reason Explanation */}
        <div
          style={{
            padding: "14px 16px",
            background: "rgba(255, 255, 255, 0.03)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-subtle)",
            marginBottom: "20px"
          }}
        >
          <div style={{ fontSize: "13px", color: "#CBD5E1", lineHeight: 1.5 }}>
            {ambiguity.reason || "The query contains terms with multiple valid business interpretations."}
          </div>
        </div>

        {/* Clarification Question & Options */}
        <div style={{ marginBottom: "24px" }}>
          <label style={{ display: "block", fontSize: "14px", fontWeight: 600, color: "#FFF", marginBottom: "12px" }}>
            {ambiguity.clarification_question || "Please select the intended calculation:"}
          </label>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {ambiguity.options?.map((option, idx) => {
              const isSelected = selectedOption === option;
              const isDefault = option === ambiguity.default_option;

              return (
                <div
                  key={idx}
                  onClick={() => setSelectedOption(option)}
                  style={{
                    padding: "14px 16px",
                    borderRadius: "var(--radius-md)",
                    border: isSelected ? "1px solid #6366F1" : "1px solid var(--border-subtle)",
                    background: isSelected ? "rgba(99, 102, 241, 0.12)" : "rgba(255, 255, 255, 0.02)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    transition: "all 0.15s ease"
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <div
                      style={{
                        width: "18px",
                        height: "18px",
                        borderRadius: "50%",
                        border: isSelected ? "5px solid #6366F1" : "2px solid var(--text-subtle)",
                        background: isSelected ? "#FFF" : "transparent",
                        flexShrink: 0
                      }}
                    />
                    <span style={{ fontSize: "13.5px", fontWeight: isSelected ? 600 : 400, color: isSelected ? "#FFF" : "#CBD5E1" }}>
                      {option}
                    </span>
                  </div>

                  {isDefault && (
                    <span
                      style={{
                        fontSize: "11px",
                        fontWeight: 600,
                        color: "var(--accent-cyan)",
                        background: "rgba(6, 182, 212, 0.1)",
                        padding: "2px 8px",
                        borderRadius: "var(--radius-full)"
                      }}
                    >
                      Recommended
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Modal Actions */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: "12px" }}>
          <button className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={() => onSubmit(selectedOption, ambiguity.category)}
            disabled={!selectedOption}
          >
            <Sparkles size={16} />
            Resolve & Generate SQL
          </button>
        </div>
      </div>
    </div>
  );
}
