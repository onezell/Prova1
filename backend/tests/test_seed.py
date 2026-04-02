"""Tests for seed/mock data generation."""

from app.seed import generate_mock_emails


class TestMockData:
    def test_generates_12_emails(self):
        emails = generate_mock_emails()
        assert len(emails) == 12

    def test_all_have_required_fields(self):
        emails = generate_mock_emails()
        required = {"id", "message_id", "uid", "subject", "sender", "date", "body", "status"}
        for em in emails:
            assert required.issubset(em.keys()), f"Missing fields in {em['subject']}"

    def test_unique_ids(self):
        emails = generate_mock_emails()
        ids = [e["id"] for e in emails]
        assert len(ids) == len(set(ids))

    def test_unique_message_ids(self):
        emails = generate_mock_emails()
        msg_ids = [e["message_id"] for e in emails]
        assert len(msg_ids) == len(set(msg_ids))

    def test_categories_are_valid(self):
        valid = {"richiesta_info", "reclamo", "supporto_tecnico", "preventivo", "collaborazione", "spam", "altro"}
        emails = generate_mock_emails()
        for em in emails:
            if em.get("category"):
                assert em["category"] in valid, f"Invalid category: {em['category']}"

    def test_all_classified_have_confidence(self):
        emails = generate_mock_emails()
        for em in emails:
            if em["status"] == "classified":
                assert em["category"] is not None
                assert em["confidence"] is not None
                assert 0 <= em["confidence"] <= 1

    def test_dates_are_decreasing(self):
        emails = generate_mock_emails()
        for i in range(1, len(emails)):
            assert emails[i - 1]["date"] >= emails[i]["date"]
