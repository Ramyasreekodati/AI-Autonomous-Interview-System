from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import datetime

class ReportingService:
    @staticmethod
    def generate_report(candidate_name, results_data):
        filename = f"RecruitAI_Report_{candidate_name.replace(' ', '_')}.pdf"
        # Always save to a predictable locations
        report_path = os.path.join(os.getcwd(), filename)
        
        c = canvas.Canvas(report_path, pagesize=letter)
        width, height = letter
        
        # Header - Premium Rect
        c.setFillColorRGB(0.29, 0.56, 0.88) # #4A90E2
        c.rect(0, height-120, width, 120, fill=1)
        
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(50, height-70, "RecruitAI Assessment")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height-90, "AUTONOMOUS INTELLIGENCE REPORT")
        c.drawString(width-180, height-70, datetime.datetime.now().strftime("%B %d, %Y"))
        c.drawString(width-180, height-85, "VERIFIED SESSION")

        # Candidate Details
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height-170, f"Candidate: {candidate_name}")
        c.setFont("Helvetica", 12)
        c.drawString(50, height-190, f"Decision: {results_data.get('final_decision', 'N/A').upper()}")
        
        # Main Scores
        y = height - 250
        c.setFillColorRGB(0.95, 0.96, 0.98)
        c.roundRect(50, y-100, width-100, 120, 15, fill=1, stroke=0)
        
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(70, y, "Performance Analysis")
        
        c.setFont("Helvetica", 12)
        y -= 30
        c.drawString(70, y, f"Technical Score: {results_data.get('interview_score', 0)}/10")
        c.drawString(300, y, f"Behavioral Score: {results_data.get('behavior_score', 0)}/100")
        
        y -= 25
        c.setFont("Helvetica-Bold", 14)
        c.drawString(70, y, f"Final Aggregate: {results_data.get('final_aggregate_score', 0)}%")
        
        # Risk & Justification
        y -= 80
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Justification & Decision Insight")
        c.line(50, y-5, 300, y-5)
        
        y -= 30
        c.setFont("Helvetica", 11)
        text_obj = c.beginText(50, y)
        text_obj.setFont("Helvetica", 11)
        text_obj.setLeading(14)
        
        # Wrap justification text
        just = results_data.get('justification', 'No justification available.')
        words = just.split()
        line = ""
        for word in words:
            if len(line + " " + word) < 80:
                line += " " + word
            else:
                text_obj.textLine(line)
                line = word
        text_obj.textLine(line)
        c.drawText(text_obj)
        
        # Risk Badge
        y = 350
        risk = results_data.get('risk_level', 'LOW').upper()
        if risk == 'LOW': c.setFillColorRGB(0.1, 0.7, 0.1)
        elif risk == 'MEDIUM': c.setFillColorRGB(0.9, 0.6, 0)
        else: c.setFillColorRGB(0.8, 0.1, 0.1)
        
        c.roundRect(width-150, y, 100, 30, 8, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width-100, y+10, f"{risk} RISK")

        # Alerts List
        y -= 50
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Logged Integrity Alerts")
        c.setFont("Helvetica", 10)
        y -= 25
        for alert in results_data.get('alerts', []):
            c.drawString(70, y, f"• {alert.replace('_', ' ').capitalize()}")
            y -= 15

        # Footer
        c.setFillColorRGB(0.6, 0.6, 0.6)
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(width/2, 30, "This report is AI-generated and strictly follows localized data constraints.")
        
        c.save()
        return report_path

reporting_service = ReportingService()
