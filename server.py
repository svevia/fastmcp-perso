from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"



def get_auth_headers():
    """
    Get authentication headers from environment variables.
    Expects API_USERNAME and API_PASSWORD environment variables.
    """
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")
    
    if not username or not password:
        return {}
    
    # Create Basic Auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    return {
        "Authorization": f"Basic {encoded_credentials}"
    }

@mcp.tool()
async def estimate_real_estate_investment(
    # Acquisition parameters
    purchase_price: float = 50000.0,
    notary_rate: float = 0.08,
    renovation: float = 10000.0,
    furniture: float = 0.0,
    agency_fees: float = 0.0,
    
    # Exploitation parameters  
    rent: float = 500.0,
    vacancy_months: float = 0.5,
    management_pct: float = 0.0,
    copro_charges: float = 10.0,
    ll_insurance: float = 10.0,
    property_tax: float = 500.0,
    other_annual: float = 0.0,
    
    # Depreciation & tax parameters
    building_years: int = 30,
    furniture_years: int = 7,
    land_share: float = 0.15,
    
    # Financing parameters
    loan_years: int = 20,
    loan_rate: float = 0.035,
    loan_insurance_rate: float = 0.002,
    down_payment: float = 5000.0,
    
    # Objectives
    target_monthly_cf: float = 0.0,
    
    # Resale / IRR parameters
    resale_years: Optional[int] = None,
    resale_price: Optional[float] = None,
    
    # API endpoint configuration
    api_base_url: str = "https://estimation-immo.ams-investissements.fr"
) -> dict:
    """
    Estimate real estate investment profitability using the estimateur-immo API. If not data is specified for some fields, use the default value
    
    Args:
        purchase_price: Property purchase price in euros
        notary_rate: Notary fees rate (default 0.08 = 8%)
        renovation: Renovation costs in euros
        furniture: Furniture costs in euros  
        agency_fees: Real estate agency fees in euros
        rent: Monthly rent in euros
        vacancy_months: Average vacancy months per year
        management_pct: Property management fee percentage (0.0-1.0)
        copro_charges: Monthly co-ownership charges in euros
        ll_insurance: Monthly landlord insurance in euros
        property_tax: Annual property tax in euros
        other_annual: Other annual expenses in euros
        building_years: Building depreciation period in years
        furniture_years: Furniture depreciation period in years
        land_share: Land share of total price (non-depreciable)
        loan_years: Loan duration in years
        loan_rate: Annual loan interest rate (0.035 = 3.5%)
        loan_insurance_rate: Annual loan insurance rate
        down_payment: Down payment amount in euros
        target_monthly_cf: Target monthly cash flow in euros
        resale_years: Years before resale (default = loan_years)
        resale_price: Resale price (default = purchase_price + renovation)
        api_base_url: Base URL of the estimateur-immo API
        
    Returns:
        Dictionary containing the investment analysis results including:
        - Acquisition costs (notary, total_cost)
        - Financing details (loan_amount, monthly_loan, etc.)
        - Exploitation metrics (collected_rent_monthly, operating_monthly, noi)
        - Tax calculations (amort_annual, taxable_profit, corporate_tax)
        - Results (annual_cashflow, monthly_cashflow, yields, DSCR)
        - Target pricing (price_for_target_cf)
        - IRR analysis (tri)
    """
    
    # Prepare the payload for the API
    payload = {
        "purchasePrice": purchase_price,
        "notaryRate": notary_rate,
        "renovation": renovation,
        "furniture": furniture,
        "agencyFees": agency_fees,
        "rent": rent,
        "vacancyMonths": vacancy_months,
        "managementPct": management_pct,
        "coproCharges": copro_charges,
        "llInsurance": ll_insurance,
        "propertyTax": property_tax,
        "otherAnnual": other_annual,
        "buildingYears": building_years,
        "furnitureYears": furniture_years,
        "landShare": land_share,
        "loanYears": loan_years,
        "loanRate": loan_rate,
        "loanInsuranceRate": loan_insurance_rate,
        "downPayment": down_payment,
        "targetMonthlyCf": target_monthly_cf,
        "resaleYears": resale_years,
        "resalePrice": resale_price
    }
    
    # Remove None values from payload
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        # Prepare headers with authentication
        headers = {"Content-Type": "application/json"}
        headers.update(get_auth_headers())
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base_url}/api/estimate",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPError as e:
        return {
            "error": f"HTTP error occurred: {str(e)}",
            "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        }
    except Exception as e:
        return {
            "error": f"An error occurred: {str(e)}"
        }


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)