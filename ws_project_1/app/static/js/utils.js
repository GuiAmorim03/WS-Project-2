// Function to determine if a color is light
function isLightColor(color) {
    
    // Add a fallback for empty values
    if (!color || color === '') {
        console.warn("Empty color value provided");
        console.groupEnd();
        return false;
    }
    
    // Remove any leading/trailing spaces
    color = color.trim();
    
    let r, g, b;
    
    try {
        // Handle hex colors with # prefix
        if (color.startsWith('#')) {
            color = color.substring(1);
        }
        
        // Try a different approach if we're still having issues
        if (color.match(/^[0-9A-Fa-f]{6}$/)) {
            r = parseInt(color.substring(0, 2), 16);
            g = parseInt(color.substring(2, 4), 16);
            b = parseInt(color.substring(4, 6), 16);
        } else if (color.match(/^[0-9A-Fa-f]{3}$/)) {
            r = parseInt(color.charAt(0) + color.charAt(0), 16);
            g = parseInt(color.charAt(1) + color.charAt(1), 16);
            b = parseInt(color.charAt(2) + color.charAt(2), 16);
        } else {
            
            // Try RGB format
            const rgbMatch = color.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
            if (rgbMatch) {
                r = parseInt(rgbMatch[1]);
                g = parseInt(rgbMatch[2]);
                b = parseInt(rgbMatch[3]);
            } else {
                console.error("Unable to parse color format:", color);
                console.groupEnd();
                return false;
            }
        }
        
        
        // Calculate luminance - if high, it's a light color
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        const isLight = luminance > 0.7;
        console.groupEnd();
        return isLight;
    } catch (e) {
        console.error("Error parsing color:", e);
        console.groupEnd();
        return false;
    }
}

function createLighterColor(hexColor) {
    try {
        hexColor = hexColor.replace('#', '');
        
        const r = parseInt(hexColor.substring(0, 2), 16);
        const g = parseInt(hexColor.substring(2, 4), 16);
        const b = parseInt(hexColor.substring(4, 6), 16);
        
        const lighterR = Math.min(255, r + 60);
        const lighterG = Math.min(255, g + 60);
        const lighterB = Math.min(255, b + 60);
        
        const lighterColor = `#${lighterR.toString(16).padStart(2, '0')}${lighterG.toString(16).padStart(2, '0')}${lighterB.toString(16).padStart(2, '0')}`;
        return lighterColor;
    } catch (e) {
        console.error("Error creating gradient:", e);
        return hexColor;
    }
}

// New function to create darker color variant for light colors
function createDarkerColor(hexColor) {
    try {
        hexColor = hexColor.replace('#', '');
        
        const r = parseInt(hexColor.substring(0, 2), 16);
        const g = parseInt(hexColor.substring(2, 4), 16);
        const b = parseInt(hexColor.substring(4, 6), 16);
        
        const darkerR = Math.max(0, r - 60);
        const darkerG = Math.max(0, g - 60);
        const darkerB = Math.max(0, b - 60);
        
        const darkerColor = `#${darkerR.toString(16).padStart(2, '0')}${darkerG.toString(16).padStart(2, '0')}${darkerB.toString(16).padStart(2, '0')}`;
        return darkerColor;
    } catch (e) {
        console.error("Error creating darker gradient:", e);
        return hexColor;
    }
}