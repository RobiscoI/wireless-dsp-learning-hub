function exportgraphics(obj, filename, varargin)
%EXPORTGRAPHICS  Stand-in for releases before R2020a, built on PRINT.
%   exportgraphics(obj, filename)                     obj: figure or axes
%   exportgraphics(obj, filename, 'Resolution', dpi)  default 150 dpi
%
%   Added by setup_path only when the real function is missing.
%   Differences from the real function:
%     - an axes argument saves its whole figure, not just the axes
%     - other name-value options are accepted and ignored
%     - App Designer figures (uifigure) cannot be printed on old releases

resolution = 150;
for k = 1:2:numel(varargin) - 1
    if strcmpi(char(varargin{k}), 'Resolution')
        resolution = varargin{k + 1};
    end
end

fig = ancestor(obj, 'figure');
if isempty(fig)
    error('compat:exportgraphics:target', 'Expected a figure or axes handle.');
end

filename = char(filename);
[~, ~, ext] = fileparts(filename);
switch lower(ext)
    case '.png'
        device = '-dpng';
    case {'.jpg', '.jpeg'}
        device = '-djpeg';
    case {'.tif', '.tiff'}
        device = '-dtiff';
    case '.pdf'
        device = '-dpdf';
    case '.eps'
        device = '-depsc';
    case '.emf'
        device = '-dmeta';
    otherwise
        error('compat:exportgraphics:format', 'Unsupported file type "%s".', ext);
end

set(fig, 'PaperPositionMode', 'auto');
print(fig, filename, device, sprintf('-r%d', round(resolution)));
end
