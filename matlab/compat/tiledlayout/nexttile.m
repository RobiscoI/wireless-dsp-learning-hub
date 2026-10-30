function ax = nexttile(varargin)
%NEXTTILE  Stand-in for releases before R2019b: next SUBPLOT of the TILEDLAYOUT grid.
%   nexttile       next tile in row-major order
%   nexttile(k)    tile k (row-major, same numbering as subplot)
%   nexttile(t)    t is the struct returned by the TILEDLAYOUT stand-in
%
%   Added by setup_path only when the real function is missing.
%   Spans such as nexttile([r c]) are not supported.

args = varargin;
fig = gcf;
if ~isempty(args) && isstruct(args{1}) && isfield(args{1}, 'Parent')
    fig = args{1}.Parent;
    args(1) = [];
end
grid = getappdata(fig, 'compat_tiled_grid');
if isempty(grid)
    error('compat:nexttile:layout', 'Call tiledlayout(m, n) before nexttile.');
end
if ~isempty(args)
    k = args{1};
    if ~isnumeric(k) || ~isscalar(k)
        error('compat:nexttile:span', 'Only nexttile or nexttile(k) is supported on this release.');
    end
else
    k = getappdata(fig, 'compat_tiled_next');
end
figure(fig);
h = subplot(grid(1), grid(2), k);
setappdata(fig, 'compat_tiled_next', k + 1);
if nargout > 0
    ax = h;
end
end
