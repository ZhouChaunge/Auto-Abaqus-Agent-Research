"""Knowledge base API endpoints."""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from abaqusgpt.knowledge.error_codes import ERROR_DATABASE, get_error_info, get_errors_by_category
from abaqusgpt.knowledge.element_library import ELEMENT_LIBRARY

router = APIRouter()


class ErrorInfo(BaseModel):
    """Error information model."""
    pattern: str
    category: str
    severity: str
    causes: List[str]
    solutions: List[str]
    reference: Optional[str] = None


class SearchResult(BaseModel):
    """Search result model."""
    type: str  # error, element, material, etc.
    title: str
    content: str
    relevance: float


@router.get("/errors", response_model=List[ErrorInfo])
async def list_errors(
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """
    List known Abaqus error codes and solutions.
    
    Categories:
    - convergence: 收敛问题
    - contact: 接触问题
    - element: 单元问题
    - material: 材料问题
    - stability: 稳定性问题
    - singularity: 奇异性问题
    """
    if category:
        errors = get_errors_by_category(category)
    else:
        errors = [{"pattern": k, **v} for k, v in ERROR_DATABASE.items()]
    
    return errors


@router.get("/errors/{pattern}")
async def get_error(pattern: str):
    """Get information about a specific error pattern."""
    # Search for matching error
    for key, info in ERROR_DATABASE.items():
        if pattern.upper() in key:
            return {"pattern": key, **info}
    
    raise HTTPException(status_code=404, detail=f"Error pattern '{pattern}' not found")


@router.get("/elements")
async def list_elements(
    dimension: Optional[str] = Query(None, description="Filter by dimension: 3, shell, beam"),
    integration: Optional[str] = Query(None, description="Filter by integration: full, reduced"),
):
    """List available element types."""
    elements = []
    
    for name, info in ELEMENT_LIBRARY.items():
        # Apply filters
        if dimension:
            if str(info.get("dimensions")) != dimension:
                continue
        if integration:
            if info.get("integration") != integration:
                continue
        
        elements.append({"type": name, **info})
    
    return elements


@router.get("/search")
async def search_knowledge(
    query: str = Query(..., description="Search query"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(10, description="Maximum results"),
):
    """
    Search across all knowledge bases.
    
    Searches errors, elements, materials, and domain-specific knowledge.
    """
    results = []
    query_upper = query.upper()
    
    # Search errors
    for pattern, info in ERROR_DATABASE.items():
        if query_upper in pattern or any(query.lower() in cause.lower() for cause in info["causes"]):
            results.append(SearchResult(
                type="error",
                title=pattern,
                content="; ".join(info["causes"][:2]),
                relevance=0.9 if query_upper in pattern else 0.7,
            ))
    
    # Search elements
    for name, info in ELEMENT_LIBRARY.items():
        if query_upper in name or query.lower() in info.get("name_cn", "").lower():
            results.append(SearchResult(
                type="element",
                title=name,
                content=info.get("name_cn", info.get("name", "")),
                relevance=0.9 if query_upper in name else 0.7,
            ))
    
    # Sort by relevance and limit
    results.sort(key=lambda x: x.relevance, reverse=True)
    return results[:limit]


@router.get("/domains/{domain}")
async def get_domain_knowledge(
    domain: str,
    topic: Optional[str] = Query(None, description="Specific topic within domain"),
):
    """
    Get domain-specific knowledge.
    
    Domains: geotechnical, structural, mechanical, thermal, impact, composite, biomechanics, electromagnetic
    """
    # TODO: Implement domain-specific knowledge retrieval
    domain_info = {
        "geotechnical": {
            "name": "岩土工程",
            "topics": ["soil_models", "rock_mechanics", "tunneling", "foundation"],
            "common_elements": ["C3D8R", "C3D4", "C3D10M"],
            "common_materials": ["Mohr-Coulomb", "Drucker-Prager", "Cam-Clay"],
        },
        "structural": {
            "name": "结构工程",
            "topics": ["concrete", "steel", "seismic", "progressive_collapse"],
            "common_elements": ["C3D8R", "S4R", "B31", "T3D2"],
            "common_materials": ["Concrete Damaged Plasticity", "Steel Plasticity"],
        },
        "mechanical": {
            "name": "机械工程",
            "topics": ["contact", "gears", "bearings", "fatigue"],
            "common_elements": ["C3D8R", "C3D20R", "C3D10M"],
            "common_materials": ["Elastic", "Plastic", "Johnson-Cook"],
        },
    }
    
    if domain not in domain_info:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
    
    return domain_info[domain]
