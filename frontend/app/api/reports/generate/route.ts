import { NextRequest, NextResponse } from 'next/server';
import puppeteer from 'puppeteer';

export async function POST(req: NextRequest) {
  try {
    const { applicantId, authState } = await req.json();

    if (!applicantId) {
      return NextResponse.json(
        { error: 'Applicant ID is required' },
        { status: 400 }
      );
    }

    // 1. Fetch Applicant Data to get loan details
    const backendUrl = process.env.NEXT_PUBLIC_API_URL;
    
    // Extract token from authState (handle different state structures)
    const token = authState?.token || authState?.state?.token;
    
    if (!token) {
        console.error('Unauthorized: No token provided in authState');
        return NextResponse.json({ error: 'Unauthorized: No token provided' }, { status: 401 });
    }

    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };

    // A. Get Applicant Details
    const applicantResponse = await fetch(`${backendUrl}/api/applicants/${applicantId}`, { headers });
    
    if (!applicantResponse.ok) {
        return NextResponse.json({ error: 'Failed to fetch applicant details' }, { status: applicantResponse.status });
    }
    
    const applicantData = await applicantResponse.json();
    const applicant = applicantData.data;

    // B. Get Eligibility/Reasoning Data
    // We call the eligibility endpoint to get the fresh reasoning and risk factors
    const predictionResponse = await fetch(`${backendUrl}/api/predictions/eligibility`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            applicant_id: applicantId,
            loan_amount: applicant.loan_amount,
            loan_term_months: applicant.loan_term_months,
            monthly_income: applicant.monthly_income
        })
    });

    if (!predictionResponse.ok) {
        return NextResponse.json({ error: 'Failed to fetch prediction data' }, { status: predictionResponse.status });
    }

    const predictionData = await predictionResponse.json();
    const data = predictionData.data;
    const reasoning = data.reasoning;
    const decision = data.decision;

    // C. Generate HTML Report (Client-side generation to bypass backend reload issues)
    const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #fff; color: #333; }
            .container { max-width: 900px; margin: 0 auto; border: 1px solid #ddd; padding: 40px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
            .header { border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
            .title { font-size: 28px; font-weight: bold; color: #2c3e50; }
            .meta { color: #7f8c8d; font-size: 14px; margin-top: 5px; }
            .badge { padding: 8px 16px; border-radius: 4px; color: white; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
            .badge-approve { background-color: #27ae60; }
            .badge-reject { background-color: #c0392b; }
            .section { margin-bottom: 40px; }
            .section-title { font-size: 18px; font-weight: 600; color: #34495e; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
            .factor-card { padding: 15px; background: #f8f9fa; border-left: 4px solid #ccc; margin-bottom: 10px; }
            .factor-risk { border-left-color: #e74c3c; background: #fdf2f2; }
            .factor-favor { border-left-color: #2ecc71; background: #f0fbf4; }
            .factor-name { font-weight: bold; margin-bottom: 5px; display: block; }
            .factor-desc { font-size: 13px; color: #555; }
            .score-box { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; margin-bottom: 30px; }
            .score-val { font-size: 36px; font-weight: bold; color: #2c3e50; }
            .score-label { font-size: 14px; color: #7f8c8d; text-transform: uppercase; }
            .bar-container { margin-top: 5px; background: #eee; height: 6px; border-radius: 3px; overflow: hidden; }
            .bar-fill { height: 100%; }
            .bar-red { background: #e74c3c; }
            .bar-green { background: #2ecc71; }
            .footer { margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; text-align: center; font-size: 12px; color: #aaa; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <div class="title">Automated Risk Assessment</div>
                    <div class="meta">Applicant: ${applicant.first_name} ${applicant.last_name} | ID: ${applicantId}</div>
                    <div class="meta">Date: ${new Date().toLocaleDateString()}</div>
                </div>
                <div class="badge ${decision.eligible ? 'badge-approve' : 'badge-reject'}">
                    ${decision.status}
                </div>
            </div>
            <div class="section">
                <div class="section-title">Executive Summary</div>
                <p style="font-size: 16px; line-height: 1.6;">${reasoning.summary}</p>
            </div>

            <div class="section">
                <div class="section-title">Key Decision Factors</div>
                <div class="grid">
                    <div>
                        <h4 style="color: #c0392b; margin-top: 0;">⚠️ Risk Factors</h4>
                        ${reasoning.risk_factors.length === 0 ? '<p style="color: #7f8c8d; font-style: italic;">No significant risk factors identified.</p>' : ''}
                        ${reasoning.risk_factors.map((f: any) => `
                            <div class="factor-card factor-risk" style="padding: 15px; border-left: 4px solid #e74c3c; background: #fdf2f2; margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                    <strong style="font-size: 14px; color: #c0392b;">${f.factor_name || f.feature_name || 'Risk Factor'}</strong>
                                    <span style="font-size: 11px; color: #e74c3c; text-transform: uppercase;">${f.severity || 'Medium'} Impact</span>
                                </div>
                                <div style="width: 100%; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; margin-bottom: 8px;">
                                    <div style="height: 100%; background: #e74c3c; width: ${f.severity === 'major' || f.influence_strength > 0.5 ? '85%' : '45%'}"></div>
                                </div>
                                <div style="font-size: 12px; color: #555;">${f.impact_description || f.explanation || ''}</div>
                            </div>
                        `).join('')}
                    </div>
                    <div>
                        <h4 style="color: #27ae60; margin-top: 0;">✅ Protective Factors</h4>
                        ${reasoning.protective_factors.length === 0 ? '<p style="color: #7f8c8d; font-style: italic;">No significant protective factors identified.</p>' : ''}
                        ${reasoning.protective_factors.map((f: any) => `
                            <div class="factor-card factor-favor" style="padding: 15px; border-left: 4px solid #2ecc71; background: #f0fbf4; margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                    <strong style="font-size: 14px; color: #27ae60;">${f.factor_name || f.feature_name || 'Protective Factor'}</strong>
                                    <span style="font-size: 11px; color: #2ecc71; text-transform: uppercase;">${f.severity || 'Positive'} Impact</span>
                                </div>
                                <div style="width: 100%; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; margin-bottom: 8px;">
                                    <div style="height: 100%; background: #2ecc71; width: ${f.severity === 'major' || f.influence_strength > 0.5 ? '85%' : '45%'}"></div>
                                </div>
                                <div style="font-size: 12px; color: #555;">${f.impact_description || f.explanation || ''}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>

            ${reasoning.suggestions && reasoning.suggestions.length > 0 ? `
            <div class="section">
                <div class="section-title">Recommendations (Action Plan)</div>
                <ul style="padding-left: 20px;">
                    ${reasoning.suggestions.map((s: any) => `
                        <li style="margin-bottom: 15px; color: #34495e; line-height: 1.5;">
                            <strong style="display: block; margin-bottom: 2px;">${s.action || s}</strong>
                            ${s.reason ? `<span style="font-size: 13px; color: #7f8c8d;">Reason: ${s.reason}</span>` : ''}
                            ${s.expected_improvement ? `<br><span style="font-size: 13px; color: #27ae60;">Expected Impact: ${s.expected_improvement}</span>` : ''}
                        </li>
                    `).join('')}
                </ul>
            </div>
            ` : ''}

            <div class="footer">
                Generated by LoanWise v4.0 • ${new Date().toISOString()}
            </div>
        </div>
    </body>
    </html>
    `;

    // 2. Launch Puppeteer to render the HTML
    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();
    
    // Set the content directly from the LIME HTML
    await page.setContent(htmlContent, { waitUntil: 'networkidle0' });

    // Generate PDF
    const pdfBuffer = await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: {
        top: '10mm',
        bottom: '10mm',
        left: '10mm',
        right: '10mm',
      },
    });

    await browser.close();

    // Return the PDF as a stream/response
    return new NextResponse(pdfBuffer as any, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="LIME_Report_${applicantId}.pdf"`,
      },
    });
  } catch (error) {
    console.error('PDF Generation Error:', error);
    return NextResponse.json(
      { error: 'Failed to generate PDF' },
      { status: 500 }
    );
  }
}
