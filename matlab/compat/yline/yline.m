function h = yline(varargin)
%YLINE  Stand-in for releases before R2018b: horizontal reference line(s).
%   yline(y)  yline(y, LineSpec)  yline(y, LineSpec, label)  yline(ax, ...)
%
%   Added by setup_path only when the real function is missing.
%   The line spans the x-limits at call time and those limits are then kept,
%   unlike the real constant line that follows later zooming. The line is
%   left out of legends.

args = varargin;
if ~isempty(args) && isscalar(args{1}) && isa(args{1}, 'matlab.graphics.axis.Axes')
    ax = args{1};
    args(1) = [];
else
    ax = gca;
end
if isempty(args)
    error('compat:yline:value', 'yline needs a y value.');
end
y = args{1};
spec = '-';
label = '';
if numel(args) >= 2
    spec = char(args{2});
end
if numel(args) >= 3
    label = char(args{3});
end

held = ishold(ax);
hold(ax, 'on');
xl = get(ax, 'XLim');
lines = gobjects(numel(y), 1);
for k = 1:numel(y)
    lines(k) = plot(ax, xl, [y(k) y(k)], spec, 'HandleVisibility', 'off');
    if ~isempty(label)
        text(ax, xl(2), y(k), label, 'HorizontalAlignment', 'right', ...
            'VerticalAlignment', 'bottom');
    end
end
set(ax, 'XLim', xl);
if ~held
    hold(ax, 'off');
end
if nargout > 0
    h = lines;
end
end
