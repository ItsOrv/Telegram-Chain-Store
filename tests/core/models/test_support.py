import pytest
from datetime import datetime
from src.core.models.support import (
    Ticket, TicketCategory, TicketPriority,
    TicketStatus, TicketComment, TicketAttachment,
    TicketHistory, TicketAssignment, TicketTag,
    TicketNote
)

def test_ticket_creation():
    ticket = Ticket(
        id=1,
        user_id=100,
        category_id=1,
        priority="high",
        subject="Payment Issue",
        description="Unable to process payment",
        status="open",
        created_at=datetime.now()
    )
    
    assert ticket.id == 1
    assert ticket.user_id == 100
    assert ticket.category_id == 1
    assert ticket.priority == "high"
    assert ticket.subject == "Payment Issue"
    assert ticket.description == "Unable to process payment"
    assert ticket.status == "open"
    assert isinstance(ticket.created_at, datetime)

def test_ticket_category_creation():
    category = TicketCategory(
        id=1,
        name="Payment",
        description="Payment related issues",
        is_active=True,
        order=1
    )
    
    assert category.id == 1
    assert category.name == "Payment"
    assert category.description == "Payment related issues"
    assert category.is_active is True
    assert category.order == 1

def test_ticket_priority_creation():
    priority = TicketPriority(
        id=1,
        name="High",
        description="High priority issues",
        color="#FF0000",
        order=1
    )
    
    assert priority.id == 1
    assert priority.name == "High"
    assert priority.description == "High priority issues"
    assert priority.color == "#FF0000"
    assert priority.order == 1

def test_ticket_status_creation():
    status = TicketStatus(
        id=1,
        name="Open",
        description="New ticket",
        color="#00FF00",
        order=1
    )
    
    assert status.id == 1
    assert status.name == "Open"
    assert status.description == "New ticket"
    assert status.color == "#00FF00"
    assert status.order == 1

def test_ticket_comment_creation():
    comment = TicketComment(
        id=1,
        ticket_id=1,
        user_id=100,
        content="Please check your payment details",
        is_internal=False,
        created_at=datetime.now()
    )
    
    assert comment.id == 1
    assert comment.ticket_id == 1
    assert comment.user_id == 100
    assert comment.content == "Please check your payment details"
    assert comment.is_internal is False
    assert isinstance(comment.created_at, datetime)

def test_ticket_attachment_creation():
    attachment = TicketAttachment(
        id=1,
        ticket_id=1,
        comment_id=1,
        file_name="payment_screenshot.png",
        file_path="/path/to/file.png",
        file_size=1024,
        mime_type="image/png",
        created_at=datetime.now()
    )
    
    assert attachment.id == 1
    assert attachment.ticket_id == 1
    assert attachment.comment_id == 1
    assert attachment.file_name == "payment_screenshot.png"
    assert attachment.file_path == "/path/to/file.png"
    assert attachment.file_size == 1024
    assert attachment.mime_type == "image/png"
    assert isinstance(attachment.created_at, datetime)

def test_ticket_history_creation():
    history = TicketHistory(
        id=1,
        ticket_id=1,
        field="status",
        old_value="open",
        new_value="in_progress",
        changed_by=100,
        changed_at=datetime.now()
    )
    
    assert history.id == 1
    assert history.ticket_id == 1
    assert history.field == "status"
    assert history.old_value == "open"
    assert history.new_value == "in_progress"
    assert history.changed_by == 100
    assert isinstance(history.changed_at, datetime)

def test_ticket_assignment_creation():
    assignment = TicketAssignment(
        id=1,
        ticket_id=1,
        user_id=100,
        assigned_by=101,
        assigned_at=datetime.now()
    )
    
    assert assignment.id == 1
    assert assignment.ticket_id == 1
    assert assignment.user_id == 100
    assert assignment.assigned_by == 101
    assert isinstance(assignment.assigned_at, datetime)

def test_ticket_tag_creation():
    tag = TicketTag(
        id=1,
        name="urgent",
        description="Urgent tickets",
        color="#FF0000"
    )
    
    assert tag.id == 1
    assert tag.name == "urgent"
    assert tag.description == "Urgent tickets"
    assert tag.color == "#FF0000"

def test_ticket_note_creation():
    note = TicketNote(
        id=1,
        ticket_id=1,
        user_id=100,
        content="Customer reported similar issue last week",
        is_private=True,
        created_at=datetime.now()
    )
    
    assert note.id == 1
    assert note.ticket_id == 1
    assert note.user_id == 100
    assert note.content == "Customer reported similar issue last week"
    assert note.is_private is True
    assert isinstance(note.created_at, datetime) 