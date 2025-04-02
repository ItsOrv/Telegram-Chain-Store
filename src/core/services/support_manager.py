from typing import Dict, Any, List
from datetime import datetime
from src.core.exceptions import ValidationError
from src.core.models import SupportTicket, FAQ

class SupportManager:
    def __init__(self):
        self.tickets = []
        self.faqs = []

    def create_ticket(self, ticket_data: Dict[str, Any]) -> SupportTicket:
        """Create a new support ticket"""
        try:
            # Validate ticket data
            if not ticket_data.get('user_id'):
                raise ValidationError("User ID is required")
            if not ticket_data.get('description'):
                raise ValidationError("Description is required")
            
            # Create ticket
            ticket = SupportTicket(
                user_id=ticket_data['user_id'],
                description=ticket_data['description'],
                status=ticket_data.get('status', 'open'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save ticket
            self.tickets.append(ticket)
            
            return ticket
        except Exception as e:
            raise ValidationError(f"Error creating ticket: {str(e)}")

    def get_ticket(self, ticket_id: int) -> SupportTicket:
        """Get ticket by ID"""
        for ticket in self.tickets:
            if ticket.id == ticket_id:
                return ticket
        return None

    def get_user_tickets(self, user_id: int) -> List[SupportTicket]:
        """Get all tickets for a user"""
        return [ticket for ticket in self.tickets if ticket.user_id == user_id]

    def update_ticket_status(self, ticket_id: int, status: str) -> SupportTicket:
        """Update ticket status"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            raise ValidationError("Ticket not found")
        
        ticket.status = status
        ticket.updated_at = datetime.utcnow()
        
        return ticket

    def add_faq(self, faq_data: Dict[str, Any]) -> FAQ:
        """Add a new FAQ"""
        try:
            # Validate FAQ data
            if not faq_data.get('question'):
                raise ValidationError("Question is required")
            if not faq_data.get('answer'):
                raise ValidationError("Answer is required")
            
            # Create FAQ
            faq = FAQ(
                question=faq_data['question'],
                answer=faq_data['answer'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save FAQ
            self.faqs.append(faq)
            
            return faq
        except Exception as e:
            raise ValidationError(f"Error adding FAQ: {str(e)}")

    def get_faqs(self) -> List[FAQ]:
        """Get all FAQs"""
        return self.faqs

    def get_faq(self, faq_id: int) -> FAQ:
        """Get FAQ by ID"""
        for faq in self.faqs:
            if faq.id == faq_id:
                return faq
        return None

    def update_faq(self, faq_id: int, faq_data: Dict[str, Any]) -> FAQ:
        """Update FAQ"""
        faq = self.get_faq(faq_id)
        if not faq:
            raise ValidationError("FAQ not found")
        
        if faq_data.get('question'):
            faq.question = faq_data['question']
        if faq_data.get('answer'):
            faq.answer = faq_data['answer']
        
        faq.updated_at = datetime.utcnow()
        
        return faq

    def delete_faq(self, faq_id: int) -> bool:
        """Delete FAQ"""
        faq = self.get_faq(faq_id)
        if not faq:
            raise ValidationError("FAQ not found")
        
        self.faqs.remove(faq)
        return True

    def get_ticket_statistics(self) -> Dict[str, Any]:
        """Get ticket statistics"""
        total_tickets = len(self.tickets)
        open_tickets = len([t for t in self.tickets if t.status == 'open'])
        closed_tickets = len([t for t in self.tickets if t.status == 'closed'])
        
        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "closed_tickets": closed_tickets,
            "resolution_rate": (closed_tickets / total_tickets * 100) if total_tickets > 0 else 0
        } 