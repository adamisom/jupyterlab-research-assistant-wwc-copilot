import { AppEvents } from '../events';

describe('AppEvents', () => {
  beforeEach(() => {
    // Clear any existing event listeners
    window.removeEventListener(
      AppEvents.OPEN_SYNTHESIS_WORKBENCH,
      () => {}
    );
    window.removeEventListener(AppEvents.OPEN_WWC_COPILOT, () => {});
  });

  describe('dispatchOpenSynthesisWorkbench', () => {
    it('should dispatch event with paper IDs', () => {
      const handler = jest.fn();
      window.addEventListener(
        AppEvents.OPEN_SYNTHESIS_WORKBENCH,
        ((event: CustomEvent) => {
          handler(event.detail);
        }) as EventListener
      );

      const paperIds = [1, 2, 3];
      AppEvents.dispatchOpenSynthesisWorkbench(paperIds);

      expect(handler).toHaveBeenCalledWith({ paperIds });
    });
  });

  describe('dispatchOpenWWCCopilot', () => {
    it('should dispatch event with paper ID and title', () => {
      const handler = jest.fn();
      window.addEventListener(
        AppEvents.OPEN_WWC_COPILOT,
        ((event: CustomEvent) => {
          handler(event.detail);
        }) as EventListener
      );

      const paperId = 42;
      const paperTitle = 'Test Paper';
      AppEvents.dispatchOpenWWCCopilot(paperId, paperTitle);

      expect(handler).toHaveBeenCalledWith({
        paperId,
        paperTitle
      });
    });
  });

  describe('onOpenSynthesisWorkbench', () => {
    it('should register event listener and return cleanup function', () => {
      const handler = jest.fn();
      const cleanup = AppEvents.onOpenSynthesisWorkbench(handler);

      const paperIds = [1, 2];
      AppEvents.dispatchOpenSynthesisWorkbench(paperIds);

      expect(handler).toHaveBeenCalledWith({ paperIds });

      cleanup();
      AppEvents.dispatchOpenSynthesisWorkbench([3, 4]);

      // Should not be called again after cleanup
      expect(handler).toHaveBeenCalledTimes(1);
    });
  });

  describe('onOpenWWCCopilot', () => {
    it('should register event listener and return cleanup function', () => {
      const handler = jest.fn();
      const cleanup = AppEvents.onOpenWWCCopilot(handler);

      const paperId = 10;
      const paperTitle = 'Another Paper';
      AppEvents.dispatchOpenWWCCopilot(paperId, paperTitle);

      expect(handler).toHaveBeenCalledWith({ paperId, paperTitle });

      cleanup();
      AppEvents.dispatchOpenWWCCopilot(20, 'Third Paper');

      // Should not be called again after cleanup
      expect(handler).toHaveBeenCalledTimes(1);
    });
  });
});

