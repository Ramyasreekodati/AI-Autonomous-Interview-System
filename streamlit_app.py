import streamlit as st
import datetime
import os
import sys

# --- BACKEND PATH CONFIG ---
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

try:
    from services.ai_engine import ai_engine
    from services.surveillance import surveillance
    from services.reporting import reporting_service
except ImportError:
    st.error("Missing architecture services.")
    st.stop()

# --------------------------------------------------
# SYSTEM ARCHITECTURE: PHASE MANAGER CLASS
# (CODE CONTROLS THE SYSTEM)
# --------------------------------------------------

class PhaseManager:
    """
    Enforces the strict 5-Phase architecture through Python logic.
    Decouples the system flow from AI prompts.
    """
    def __init__(self):
        self._initialize_state()

    def _initialize_state(self):
        if "phase" not in st.session_state:
            st.session_state.phase = 1
        if "db" not in st.session_state:
            st.session_state.db = {
                "questions": [],
                "answers": {}, # Index -> {text, time}
                "evals": {},
                "meta": {}
            }

    @property
    def current_phase(self):
        return st.session_state.phase

    def set_phase(self, phase_id):
        # BLOCKING LOGIC: Cannot jump ahead without data
        if phase_id == 2 and not st.session_state.db["answers"]:
            st.error("Phase 1 not complete: No answers stored.")
            return
        st.session_state.phase = phase_id
        st.rerun()

    def run_phase_1(self):
        """PHASE 1: Question Generation & Answer Storage"""
        st.header("Phase 1: Knowledge Acquisition")
        
        # Setup (If no questions yet)
        if not st.session_state.db["questions"]:
            with st.container(border=True):
                role = st.text_input("Role")
                skills = st.text_input("Skills")
                if st.button("Initialize Interview"):
                    # CODE triggers generation
                    qs = ai_engine.generate_questions_cached(role, skills, "Medium", 3)
                    st.session_state.db["questions"] = qs
                    st.session_state.db["meta"] = {"role": role, "candidate": "Candidate_A"}
                    st.rerun()
            return

        # Core Interview Loop
        qs = st.session_state.db["questions"]
        idx = len(st.session_state.db["answers"])
        
        if idx < len(qs):
            st.subheader(f"Question {idx + 1}")
            st.info(qs[idx])
            ans = st.text_area("Response", key=f"ans_{idx}")
            if st.button("Store & Next"):
                if ans.strip():
                    # INDEXED STORAGE (PHASE 1 Requirement)
                    st.session_state.db["answers"][idx] = {
                        "text": ans,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    st.rerun()
        else:
            st.success("Phase 1 complete. All data points stored in indexed DB.")
            if st.button("Proceed to Phase 2 >>"):
                self.set_phase(2)

    def run_phase_2(self):
        """PHASE 2: Automated Analysis"""
        st.header("Phase 2: Technical Evaluation")
        db = st.session_state.db
        if not db["evals"]:
            with st.spinner("Processing stored responses..."):
                for i, q in enumerate(db["questions"]):
                    ans = db["answers"][i]["text"]
                    # CODE triggers evaluation
                    db["evals"][i] = ai_engine.evaluate_answer(q, ans)
            st.success("Phase 2 Complete.")
        
        if st.button("Proceed to Phase 4 >>"):
            self.set_phase(4)

    def run_phase_4(self):
        """PHASE 4: System Integration"""
        st.header("Phase 4: Global Synthesis")
        db = st.session_state.db
        if "final" not in db:
            # CODE combines results
            res = ai_engine.generate_final_result(db["evals"], []) 
            db["final"] = res
            st.success("Phase 4 Complete: Results Integrated.")
        
        if st.button("Proceed to Phase 5: Result >>"):
            self.set_phase(5)

    def run_phase_5(self):
        """PHASE 5: Final Hiring Report"""
        st.header("Phase 5: Executive Assessment")
        res = st.session_state.db["final"]
        st.json(res)
        if st.button("Reset Architecture"):
            st.session_state.clear()
            st.rerun()

# --------------------------------------------------
# MAIN EXECUTION (ACTUAL ARCHITECTURE)
# --------------------------------------------------

st.set_page_config(page_title="RecruitAI Core Architecture")
manager = PhaseManager()

# CODE CONTROLS THE FLOW
if manager.current_phase == 1:
    manager.run_phase_1()
elif manager.current_phase == 2:
    manager.run_phase_2()
elif manager.current_phase == 4:
    manager.run_phase_4()
elif manager.current_phase == 5:
    manager.run_phase_5()
