"""
API Endpoint Tests
------------------
Tests for all REST API endpoints including auth, FIR CRUD, and legal operations.
"""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_officer_registration(self, client: AsyncClient):
        """Test officer registration request."""
        response = await client.post(
            "/api/auth/register-request",
            json={
                "name": "John Doe",
                "badge_number": "KC001",
                "rank": "Constable",
                "police_station": "Kalpakancherry",
                "district": "Kottayam",
                "phone": "9876543210",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Registration request submitted"
        assert data["registration_request"]["badge_number"] == "KC001"

    @pytest.mark.asyncio
    async def test_officer_login_success(self, authenticated_client: AsyncClient):
        """Test successful officer login."""
        # The authenticated_client already logged in, so we just verify it has a token
        assert "Authorization" in authenticated_client.headers
        assert authenticated_client.headers["Authorization"].startswith("Bearer ")

    @pytest.mark.asyncio
    async def test_officer_login_failure(self, client: AsyncClient):
        """Test login with wrong credentials."""
        response = await client.post(
            "/api/auth/login",
            json={"badge_number": "NONEXISTENT", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_officer_profile(self, authenticated_client: AsyncClient):
        """Test retrieving officer profile."""
        response = await client.get("/api/auth/me")
        # Test with authenticated client if endpoint requires auth
        # This depends on your implementation


class TestFIREndpoints:
    """Test FIR CRUD and analysis endpoints."""

    @pytest.mark.asyncio
    async def test_fir_list_empty(self, authenticated_client: AsyncClient):
        """Test listing FIRs when database is empty."""
        response = await authenticated_client.get("/api/firs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_analyze_text_narrative(self, authenticated_client: AsyncClient, sample_fir_data: dict):
        """Test analyzing a pasted FIR narrative (without saving)."""
        response = await authenticated_client.post(
            "/api/firs/analyze-text",
            json={"narrative": sample_fir_data["narrative"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "crime_type" in data
        assert "severity" in data
        assert "acts" in data
        assert data["crime_type"] in ["theft", "other", "assault", "fraud"]

    @pytest.mark.asyncio
    async def test_analyze_and_save_narrative(
        self, authenticated_client: AsyncClient, sample_fir_data: dict
    ):
        """Test analyzing and saving a new FIR narrative."""
        response = await authenticated_client.post(
            "/api/firs/analyze-and-save",
            json={
                "fir_number": "001/2025",
                "police_station": "Kalpakancherry",
                "narrative": sample_fir_data["narrative"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["fir_number"] == "001/2025"
        assert data["crime_type"] is not None

    @pytest.mark.asyncio
    async def test_get_fir_details(
        self, authenticated_client: AsyncClient, sample_fir_data: dict
    ):
        """Test retrieving FIR details by ID."""
        # First, create a FIR
        create_response = await authenticated_client.post(
            "/api/firs/analyze-and-save",
            json={
                "fir_number": "002/2025",
                "police_station": "Kalpakancherry",
                "narrative": sample_fir_data["narrative"],
            },
        )
        fir_id = create_response.json()["id"]

        # Then retrieve it
        response = await authenticated_client.get(f"/api/firs/{fir_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == fir_id
        assert data["fir_number"] == "002/2025"

    @pytest.mark.asyncio
    async def test_fir_similarity_search(
        self, authenticated_client: AsyncClient, sample_fir_data: dict
    ):
        """Test finding similar FIRs."""
        # Create a FIR first
        create_response = await authenticated_client.post(
            "/api/firs/analyze-and-save",
            json={
                "fir_number": "003/2025",
                "police_station": "Kalpakancherry",
                "narrative": "A theft case reported. Stolen items worth Rs. 5000.",
            },
        )
        fir_id = create_response.json()["id"]

        # Search for similar
        response = await authenticated_client.get(
            f"/api/firs/{fir_id}/similar?limit=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_filter_firs_by_crime_type(
        self, authenticated_client: AsyncClient
    ):
        """Test filtering FIRs by crime type."""
        # Create FIRs with different crime types
        for i in range(3):
            await authenticated_client.post(
                "/api/firs/analyze-and-save",
                json={
                    "fir_number": f"00{4+i}/2025",
                    "police_station": "Kalpakancherry",
                    "narrative": "A theft case reported. Items stolen.",
                },
            )

        response = await authenticated_client.get("/api/firs?crime_type=theft")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_filter_firs_by_police_station(
        self, authenticated_client: AsyncClient
    ):
        """Test filtering FIRs by police station."""
        response = await authenticated_client.get(
            "/api/firs?police_station=Kalpakancherry"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestLegalEndpoints:
    """Test legal assistant endpoints."""

    @pytest.mark.asyncio
    async def test_legal_query(self, authenticated_client: AsyncClient, sample_legal_query: dict):
        """Test asking a legal question."""
        response = await authenticated_client.post(
            "/api/legal/query",
            json=sample_legal_query,
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    @pytest.mark.asyncio
    async def test_legal_sections_browse(self, authenticated_client: AsyncClient):
        """Test browsing IPC/BNS sections."""
        response = await authenticated_client.get("/api/legal/sections")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_legal_section_lookup(self, authenticated_client: AsyncClient):
        """Test looking up a specific section."""
        response = await authenticated_client.get("/api/legal/sections/IPC/379")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "section_number" in data or "punishment" in data

    @pytest.mark.asyncio
    async def test_ipc_bns_equivalent_mapping(self, authenticated_client: AsyncClient):
        """Test IPC to BNS cross-mapping."""
        response = await authenticated_client.get("/api/legal/equivalent/IPC/379")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "equivalent_section" in data or "bns_section" in data

    @pytest.mark.asyncio
    async def test_punishment_calculator(self, authenticated_client: AsyncClient):
        """Test punishment calculator for sections."""
        response = await authenticated_client.post(
            "/api/legal/punishment-calc",
            json={"acts": ["IPC:379", "IPC:511"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_punishment" in data or "punishments" in data


class TestDashboardEndpoints:
    """Test dashboard statistics endpoints."""

    @pytest.mark.asyncio
    async def test_dashboard_stats(self, authenticated_client: AsyncClient):
        """Test dashboard statistics endpoint."""
        response = await authenticated_client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_firs" in data or "crime_distribution" in data


class TestMOPatternEndpoints:
    """Test Modus Operandi pattern detection endpoints."""

    @pytest.mark.asyncio
    async def test_list_mo_patterns(self, authenticated_client: AsyncClient):
        """Test listing detected MO patterns."""
        response = await authenticated_client.get("/api/mo/patterns")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_detect_mo_patterns(self, authenticated_client: AsyncClient):
        """Test running MO detection."""
        response = await authenticated_client.post("/api/mo/detect")
        assert response.status_code in [200, 202]
        data = response.json()
        assert "patterns" in data or "message" in data


class TestTranslationEndpoints:
    """Test translation endpoints."""

    @pytest.mark.asyncio
    async def test_translate_text(self, authenticated_client: AsyncClient):
        """Test translating text between Malayalam and English."""
        response = await authenticated_client.post(
            "/api/translate",
            json={"text": "A theft case", "source_lang": "en", "target_lang": "ml"},
        )
        assert response.status_code in [200, 503]  # 503 if service unavailable
        if response.status_code == 200:
            data = response.json()
            assert "translated_text" in data
