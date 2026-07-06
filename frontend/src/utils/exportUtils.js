/**
 * Export Utilities
 * ----------------
 * Functions to export data in various formats (CSV, JSON, PDF, etc.)
 */

/**
 * Export data as CSV
 */
export function exportToCSV(data, filename = 'export.csv') {
  if (!data || data.length === 0) {
    alert('No data to export');
    return;
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);

  // Create CSV content
  let csv = headers.join(',') + '\n';

  data.forEach(row => {
    const values = headers.map(header => {
      const value = row[header];
      // Escape quotes and handle special characters
      if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      return value || '';
    });
    csv += values.join(',') + '\n';
  });

  // Download
  downloadFile(csv, filename, 'text/csv');
}

/**
 * Export FIR list as CSV with specific columns
 */
export function exportFIRsToCSV(firs, filename = 'firs.csv') {
  const data = firs.map(fir => ({
    'FIR Number': fir.fir_number,
    'Police Station': fir.police_station,
    'District': fir.district,
    'Crime Type': fir.crime_type,
    'Severity': fir.severity,
    'Date': fir.fir_date || fir.created_at,
    'Summary': fir.summary_en || fir.narrative.substring(0, 100),
  }));

  exportToCSV(data, filename);
}

/**
 * Export legal sections as CSV
 */
export function exportSectionsToCSV(sections, filename = 'legal_sections.csv') {
  const data = sections.map(sec => ({
    'Act': sec.act,
    'Section': sec.section_number,
    'Description': sec.description,
    'Offense Type': sec.offense_type,
    'Cognizable': sec.cognizable ? 'Yes' : 'No',
    'Bailable': sec.bailable ? 'Yes' : 'No',
    'Punishment': sec.punishment,
  }));

  exportToCSV(data, filename);
}

/**
 * Export MO patterns as CSV
 */
export function exportPatternsToCSV(patterns, filename = 'mo_patterns.csv') {
  const data = patterns.map(pattern => ({
    'Pattern Name': pattern.pattern_name,
    'Crime Type': pattern.crime_type,
    'Occurrence Count': pattern.occurrence_count,
    'First Seen': pattern.first_seen,
    'Last Seen': pattern.last_seen,
    'Description': pattern.description,
  }));

  exportToCSV(data, filename);
}

/**
 * Export data as JSON
 */
export function exportToJSON(data, filename = 'export.json') {
  const json = JSON.stringify(data, null, 2);
  downloadFile(json, filename, 'application/json');
}

/**
 * Export data as XML
 */
export function exportToXML(data, rootElement = 'root', filename = 'export.xml') {
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
  xml += `<${rootElement}>\n`;

  if (Array.isArray(data)) {
    data.forEach(item => {
      xml += objectToXML(item, 'item', 1);
    });
  } else {
    xml += objectToXML(data, 'item', 1);
  }

  xml += `</${rootElement}>`;
  downloadFile(xml, filename, 'application/xml');
}

/**
 * Convert object to XML string
 */
function objectToXML(obj, elementName, depth = 0) {
  const indent = '  '.repeat(depth);
  let xml = '';

  if (typeof obj === 'object' && obj !== null) {
    xml += `${indent}<${elementName}>\n`;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        xml += objectToXML(obj[key], key, depth + 1);
      }
    }
    xml += `${indent}</${elementName}>\n`;
  } else {
    const value = String(obj || '').replace(/[<>&]/g, char => {
      const entities = { '<': '&lt;', '>': '&gt;', '&': '&amp;' };
      return entities[char];
    });
    xml += `${indent}<${elementName}>${value}</${elementName}>\n`;
  }

  return xml;
}

/**
 * Export as HTML table (for display/print)
 */
export function exportToHTML(data, title = 'Data Export', filename = 'export.html') {
  if (!data || data.length === 0) {
    alert('No data to export');
    return;
  }

  const headers = Object.keys(data[0]);
  let html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${title}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: #333; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    th { background-color: #4CAF50; color: white; }
    tr:nth-child(even) { background-color: #f2f2f2; }
    tr:hover { background-color: #ddd; }
    .timestamp { color: #666; font-size: 12px; }
  </style>
</head>
<body>
  <h1>${title}</h1>
  <p class="timestamp">Generated on ${new Date().toLocaleString()}</p>
  <table>
    <thead>
      <tr>
        ${headers.map(h => `<th>${h}</th>`).join('')}
      </tr>
    </thead>
    <tbody>
      ${data.map(row => `
        <tr>
          ${headers.map(h => `<td>${row[h] || ''}</td>`).join('')}
        </tr>
      `).join('')}
    </tbody>
  </table>
</body>
</html>
  `;

  downloadFile(html, filename, 'text/html');
}

/**
 * Download file helper
 */
function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Generate filename with timestamp
 */
export function generateFilename(prefix = 'export', format = 'csv') {
  const timestamp = new Date().toISOString().slice(0, 10);
  return `${prefix}_${timestamp}.${format}`;
}

/**
 * Export table data with print-friendly styling
 */
export function printData(data, title = 'Report') {
  const printWindow = window.open('', '', 'width=1000,height=700');

  let html = `
<html>
<head>
  <title>${title}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: #333; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
    th, td { border: 1px solid #333; padding: 8px; text-align: left; font-size: 11px; }
    th { background-color: #4CAF50; color: white; }
    .timestamp { color: #666; font-size: 10px; }
    @media print {
      body { margin: 0; }
      .timestamp { display: none; }
    }
  </style>
</head>
<body>
  <h1>${title}</h1>
  <p class="timestamp">Printed on ${new Date().toLocaleString()}</p>
  `;

  if (Array.isArray(data) && data.length > 0) {
    const headers = Object.keys(data[0]);
    html += '<table>';
    html += '<thead><tr>';
    headers.forEach(h => {
      html += `<th>${h}</th>`;
    });
    html += '</tr></thead>';
    html += '<tbody>';

    data.forEach(row => {
      html += '<tr>';
      headers.forEach(h => {
        html += `<td>${row[h] || ''}</td>`;
      });
      html += '</tr>';
    });

    html += '</tbody></table>';
  }

  html += '</body></html>';

  printWindow.document.write(html);
  printWindow.document.close();
  printWindow.print();
}
