function t = tiledlayout(varargin)
%TILEDLAYOUT  Stand-in for releases before R2019b: an m-by-n grid for NEXTTILE.
%   tiledlayout(m, n) remembers the grid on the current figure; NEXTTILE then
%   places axes with SUBPLOT in row-major order.
%
%   Added by setup_path only when the real function is missing.
%   Only the (m, n) form is supported. Name-value options such as
%   'TileSpacing' are ignored. The returned struct is not a layout object,
%   so calls like title(t, ...) are not available.

if numel(varargin) < 2 || ~isnumeric(varargin{1}) || ~isnumeric(varargin{2})
    error('compat:tiledlayout:form', 'Only tiledlayout(m, n) is supported on this release.');
end
grid = [varargin{1} varargin{2}];
fig = gcf;
setappdata(fig, 'compat_tiled_grid', grid);
setappdata(fig, 'compat_tiled_next', 1);
if nargout > 0
    t = struct('GridSize', grid, 'Parent', fig);
end
end
