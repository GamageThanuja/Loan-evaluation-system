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

    // Launch a headless browser
    const browser = await puppeteer.launch({
      headless: true, // Use "new" headless mode if older puppeteer, but true is standard
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();
    
    // Inject dynamic auth state into localStorage if provided
    if (authState) {
        await page.evaluateOnNewDocument((data) => {
            localStorage.setItem('auth-storage', JSON.stringify(data));
        }, authState);
    }
    
    // Determine the base URL dynamically or fallback to localhost
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';
    const reportUrl = `${baseUrl}/reports/print/${applicantId}`;

    // Navigate to the report page
    // Using networkidle0 to wait for charts/animations to likely finish
    await page.goto(reportUrl, { waitUntil: 'networkidle0' });

    // Ensure the content is ready (e.g., waiting for specific selector if needed)
    // await page.waitForSelector('#report-content'); 

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
    // Cast to any to avoid strict type checking on BodyInit with Buffer/Uint8Array in some envs
    return new NextResponse(pdfBuffer as any, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="Rejection_Report_${applicantId}.pdf"`,
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
