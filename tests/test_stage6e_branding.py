from pathlib import Path
from app.services.branding_service import company_display_name, company_contact_lines, resolve_logo
from app.services.proposal_service import build_proposal_pdf

def test_branding_and_proposal(tmp_path):
    assert company_display_name({'display_name':'ABC Solar'}) == 'ABC Solar'
    assert 'Phone: +256' in company_contact_lines({'phone':'+256'})
    logo = tmp_path / 'logo.txt'; logo.write_text('x')
    assert resolve_logo({'logo_path':str(logo)}) == str(logo)
    output = tmp_path / 'quote.pdf'
    path = build_proposal_pdf(output, company={'display_name':'ABC Solar','payment_terms':'50% advance','terms_conditions':'Valid 30 days.'}, customer={'name':'Client'}, project={'name':'Site'}, quote={'quote_currency':'USD','lines':[],'direct_cost':0,'overhead':0,'contingency':0,'markup':0,'tax':0,'grand_total':0}, quote_number='Q-001')
    assert Path(path).exists() and Path(path).stat().st_size > 0
