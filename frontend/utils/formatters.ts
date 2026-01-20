/**
 * Format a number as currency (LKR by default)
 */
export const formatCurrency = (amount: number | string | undefined | null, currency = 'LKR'): string => {
  if (amount === undefined || amount === null) return 'N/A';
  
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  
  if (isNaN(numAmount)) return 'N/A';
  
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numAmount);
};

/**
 * Format a date string
 */
export const formatDate = (dateString: string | undefined | null): string => {
  if (!dateString) return 'N/A';
  
  try {
    return new Date(dateString).toLocaleDateString('en-UK', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
  } catch (e) {
    return dateString;
  }
};
